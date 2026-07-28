"""
AgentGate RAG Engine — Pure Python BM25 (Okapi BM25)
Zero external dependencies. No pip installs required.

Architecture:
- Primary path: BM25 keyword-based ranking (always available)
- Optional enhancement: Ollama embedding API (uses urllib, stdlib-only)
- Removed: requests library, sentence_transformers (violated zero-dep promise)

BM25 is the algorithm behind Elasticsearch and Lucene.
For code retrieval, it is often more precise than embeddings
because code uses exact terms, not natural language synonyms.
"""
import os
import json
import math
import re
import hashlib
import config

# --- Embedding Cache (SHA256-keyed JSON) ---
def _load_cache():
    """Load the embedding cache from disk. Returns empty dict on any failure."""
    if not os.path.exists(config.EMBEDDINGS_CACHE_PATH):
        return {}
    try:
        with open(config.EMBEDDINGS_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _save_cache(cache, current_texts=None):
    """Persist the embedding cache to disk. Silent on failure.
    If current_texts is provided, evict keys that no longer exist."""
    if current_texts is not None:
        valid_keys = {_cache_key(text) for text in current_texts}
        cache = {k: v for k, v in cache.items() if k in valid_keys}
    try:
        os.makedirs(os.path.dirname(config.EMBEDDINGS_CACHE_PATH), exist_ok=True)
        with open(config.EMBEDDINGS_CACHE_PATH, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    except Exception:
        pass


def _cache_key(text):
    """SHA256 hash of text content, used as cache key."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

# --- Tokenizer ---
def tokenize(text):
    """Simple whitespace + punctuation tokenizer. Lowercases everything.
    Splits camelCase and snake_case terms."""
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = text.replace('_', ' ')
    tokens = re.findall(r"[a-zA-Z0-9]+", text.lower())
    return tokens

# --- BM25 Core ---
def _get_mtimes(documents):
    mtimes = {}
    for doc_id, _ in documents:
        filepath = doc_id.split(':')[0]
        try:
            mtimes[filepath] = os.path.getmtime(filepath)
        except OSError:
            pass
    return mtimes

def build_bm25_index(documents):
    """
    Build a BM25 index from a list of (filepath, text) tuples.
    Returns (idf_map, tf_map, avg_dl, doc_lengths).
    Uses caching.
    """
    current_mtimes = _get_mtimes(documents)
    
    # Try to load cached index
    if os.path.exists(config.SEARCH_INDEX_PATH):
        try:
            with open(config.SEARCH_INDEX_PATH, "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                if cached_data.get("mtimes") == current_mtimes:
                    return cached_data["idf"], cached_data["tf_map"], cached_data["avg_dl"], cached_data["doc_lengths"]
        except Exception:
            pass
    N = len(documents)
    df = {}         # doc frequency per term
    tf_map = {}     # tf_map[filepath] = {term: count}
    doc_lengths = {}

    for filepath, text in documents:
        tokens = tokenize(text)
        doc_lengths[filepath] = len(tokens)
        counts = {}
        for token in tokens:
            counts[token] = counts.get(token, 0) + 1
        tf_map[filepath] = counts
        for term in counts:
            df[term] = df.get(term, 0) + 1

    avg_dl = sum(doc_lengths.values()) / N if N > 0 else 1

    # IDF (Okapi BM25 formula)
    idf = {}
    for term, n_t in df.items():
        idf[term] = math.log((N - n_t + 0.5) / (n_t + 0.5) + 1)

    # Cache the index
    try:
        os.makedirs(os.path.dirname(config.SEARCH_INDEX_PATH), exist_ok=True)
        with open(config.SEARCH_INDEX_PATH, "w", encoding="utf-8") as f:
            json.dump({
                "mtimes": current_mtimes,
                "idf": idf,
                "tf_map": tf_map,
                "avg_dl": avg_dl,
                "doc_lengths": doc_lengths
            }, f)
    except Exception:
        pass

    return idf, tf_map, avg_dl, doc_lengths

def bm25_score(query_tokens, filepath, idf, tf_map, avg_dl, doc_lengths):
    """Score a single document against query tokens using Okapi BM25."""
    score = 0.0
    doc_tf = tf_map.get(filepath, {})
    dl = doc_lengths.get(filepath, 0)

    for token in set(query_tokens):
        if token not in idf:
            continue
        tf = doc_tf.get(token, 0)
        numerator = tf * (config.BM25_K1 + 1)
        denominator = tf + config.BM25_K1 * (1 - config.BM25_B + config.BM25_B * dl / avg_dl)
        score += idf[token] * (numerator / denominator if denominator > 0 else 0)

    return score

# --- Ollama Optional Path (stdlib-only urllib) ---
def get_embedding_ollama(text):
    """Try to get an embedding from Ollama using stdlib urllib.

    Results are cached to CACHE_FILE using SHA256 content hashing.
    Cache is loaded fresh per call so concurrent writes are respected.
    Returns the embedding vector (list of floats), or None on failure.
    """
    cache = _load_cache()
    key = _cache_key(text)
    if key in cache:
        return cache[key]

    try:
        import urllib.request
        data = json.dumps({"model": config.EMBED_MODEL, "input": text}).encode("utf-8")
        req = urllib.request.Request(config.OLLAMA_URL, data=data,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=2) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            embeddings = result.get("embeddings")
            if embeddings and len(embeddings) > 0:
                embedding = embeddings[0]
                cache[key] = embedding
                _save_cache(cache)
                return embedding
    except Exception:
        return None

def cosine_similarity(v1, v2):
    """Cosine similarity between two equal-length vectors."""
    dot = sum(a * b for a, b in zip(v1, v2))
    n1 = math.sqrt(sum(a * a for a in v1))
    n2 = math.sqrt(sum(b * b for b in v2))
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)

# --- File Loading and Chunking ---
def chunk_document(filepath, text):
    """
    Split a document into chunks. For small files, returns the whole file.
    For large files, attempts to split on class/function boundaries or blank lines.
    Returns a list of (id, chunk_text) where id is filepath:line_num.
    """
    if len(text) < 4000:  # ~1000 tokens, keep intact
        return [(filepath, text)]
    
    chunks = []
    lines = text.split('\n')
    current_chunk = []
    current_start = 1
    
    # Generic regex for major definitions across languages
    boundary_regex = re.compile(r"^(def|class|function|async function|const \w+ = \(|struct|type|func|pub fn) ")
    
    for i, line in enumerate(lines):
        if boundary_regex.match(line) and len(current_chunk) > 10:
            # Save previous chunk
            chunk_text = '\n'.join(current_chunk)
            chunks.append((f"{filepath}:{current_start}", chunk_text))
            current_chunk = []
            current_start = i + 1
        current_chunk.append(line)
        
        # Max chunk size fallback (e.g. 500 lines)
        if len(current_chunk) > 500:
            chunk_text = '\n'.join(current_chunk)
            chunks.append((f"{filepath}:{current_start}", chunk_text))
            current_chunk = []
            current_start = i + 1
            
    if current_chunk:
        chunk_text = '\n'.join(current_chunk)
        chunks.append((f"{filepath}:{current_start}", chunk_text))
        
    return chunks

def load_documents(root="."):
    """Walk the project and load all scannable text files."""
    documents = []
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in config.IGNORE_DIRS]
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()
            if ext in config.SKIP_EXTENSIONS or ext not in config.SCANNABLE_EXTS:
                continue
            filepath = os.path.join(dirpath, filename)
            try:
                if os.path.getsize(filepath) > config.MAX_FILE_SIZE:
                    continue
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
                documents.extend(chunk_document(filepath, text))
            except (UnicodeDecodeError, OSError):
                pass
    return documents

# --- Public API ---
def query_codebase(query, top_k=5, root="."):
    """
    Find the most relevant files/chunks for a query.
    Uses BM25 as a base, and Reciprocal Rank Fusion (RRF) with Ollama embeddings if available.
    Always returns results — BM25 never fails due to missing dependencies.
    """
    documents = load_documents(root)
    if not documents:
        return []

    query_tokens = tokenize(query)

    # Compute BM25 scores (always available)
    bm25_results = []
    idf, tf_map, avg_dl, doc_lengths = build_bm25_index(documents)
    for doc_id, _ in documents:
        score = bm25_score(query_tokens, doc_id, idf, tf_map, avg_dl, doc_lengths)
        if score > 0:
            bm25_results.append({"file": doc_id, "score": score, "method": "bm25"})
            
    bm25_results.sort(key=lambda x: x["score"], reverse=True)

    # Try Ollama for semantic similarity
    embed_results = []
    query_vec = get_embedding_ollama(query)
    if query_vec is not None:
        all_success = True
        for doc_id, text in documents:
            file_vec = get_embedding_ollama(text[:2000])  # Limit to 2KB for speed
            if file_vec:
                score = cosine_similarity(query_vec, file_vec)
                embed_results.append({"file": doc_id, "score": score, "method": "embedding"})
            else:
                all_success = False
                break
                
        if all_success and embed_results:
            # Save the cache after batch processing
            _save_cache(_load_cache(), current_texts=[t for _, t in documents])
            embed_results.sort(key=lambda x: x["score"], reverse=True)
            
            # Reciprocal Rank Fusion (RRF)
            rrf_scores = {}
            k = 60
            for rank, res in enumerate(bm25_results):
                rrf_scores[res["file"]] = rrf_scores.get(res["file"], 0) + 1.0 / (k + rank + 1)
            for rank, res in enumerate(embed_results):
                rrf_scores[res["file"]] = rrf_scores.get(res["file"], 0) + 1.0 / (k + rank + 1)
                
            final_results = [{"file": file, "score": score, "method": "hybrid"} for file, score in rrf_scores.items()]
            final_results.sort(key=lambda x: x["score"], reverse=True)
            return final_results[:top_k]
        else:
            config.logger.warning("Ollama embedding failed for some chunks. Falling back to pure BM25.")
    else:
        config.logger.warning("Ollama API unreachable or failed. Falling back to pure BM25.")

    return bm25_results[:top_k]

def check_arbiter(query, filepath, threshold=0.3):
    """
    MASK Arbiter: Check if a file is relevant to a query.
    Uses BM25 score normalized against top result as a 0-1 relevance signal.
    """
    if not os.path.exists(filepath):
        return False, 0.0

    results = query_codebase(query, top_k=10)
    if not results:
        return False, 0.0

    # Find this file's score in results
    file_score = 0.0
    for r in results:
        if os.path.normcase(os.path.normpath(r["file"])) == os.path.normcase(os.path.normpath(filepath)):
            file_score = r["score"]
            break

    # Normalize: score / max_score gives a 0-1 relative relevance
    max_score = results[0]["score"] if results else 1.0
    normalized = file_score / max_score if max_score > 0 else 0.0

    return normalized >= threshold, normalized
