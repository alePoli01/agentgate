import logging
import os
from utils import safe_read

logger = logging.getLogger("agentgate")

TIERS = {
    "SMALL": {
        "max_context": 31999,
        "max_iterations": 3,
        "context_gate": 40,
        "strike_threshold": 2,
        "delegation_files": 3,
        "tell_limit": 300,
        "self_critique": False,
        "darrms_mandatory": True
    },
    "MEDIUM": {
        "max_context": 127999,
        "max_iterations": 6,
        "context_gate": 55,
        "strike_threshold": 3,
        "delegation_files": 5,
        "tell_limit": 500,
        "self_critique": True,
        "darrms_mandatory": True
    },
    "LARGE": {
        "max_context": 999999999,
        "max_iterations": 10,
        "context_gate": 70,
        "strike_threshold": 4,
        "delegation_files": 8,
        "tell_limit": 1000,
        "self_critique": True,
        "darrms_mandatory": False
    }
}

def parse_model_env(filepath: str = ".ai/MODEL_ENV.md") -> dict:
    """Naive YAML parser for MODEL_ENV.md that extracts key-value pairs."""
    config = {
        "model_type": "local",
        "context_window": 8000,
        "parallel_subagents": False,
        "cost_aware": True
    }
    
    if not os.path.exists(filepath):
        logger.warning(f"MODEL_ENV.md not found at {filepath} — defaulting to SMALL tier. Run /new-project to configure.")
        return config
        
    content = safe_read(filepath)
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
            
        if ":" in line:
            key, val_str = line.split(":", 1)
            key = key.strip()
            val_str = val_str.strip()
            
            # Remove inline comments
            if "#" in val_str:
                val_str = val_str.split("#", 1)[0].strip()
                
            if key == "context_window":
                try:
                    config[key] = int(val_str)
                except ValueError:
                    logger.warning(f"Invalid context_window value '{val_str}' in {filepath}, defaulting to 8000")
            elif key in ["parallel_subagents", "cost_aware"]:
                config[key] = val_str.lower() == "true"
            elif key == "model_type":
                config[key] = val_str
                
    return config

def resolve_tier(context_window: int) -> str:
    """Resolve the tier based on context window size."""
    if context_window < 32000:
        return "SMALL"
    elif context_window < 128000:
        return "MEDIUM"
    else:
        return "LARGE"

def get_tier_config() -> dict:
    """Get the full configuration including tier rules based on MODEL_ENV.md."""
    env_config = parse_model_env()
    tier_name = resolve_tier(env_config["context_window"])
    
    # Merge env config with tier rules
    full_config = env_config.copy()
    full_config["tier"] = tier_name
    full_config.update(TIERS[tier_name])
    
    return full_config

def print_tier_info() -> None:
    """Print the tier configuration block."""
    config = get_tier_config()
    print("============================================================")
    print(f"[AGENTGATE] MODEL TIER: {config['tier']}")
    print("============================================================")
    print(f"Model Type        : {config['model_type']}")
    print(f"Context Window    : {config['context_window']}")
    print(f"Parallel Subagents: {config['parallel_subagents']}")
    print(f"Cost Aware        : {config['cost_aware']}")
    print("---")
    print(f"Max Iterations    : {config['max_iterations']}")
    print(f"Context Gate      : {config['context_gate']}%")
    print(f"Strike Threshold  : {config['strike_threshold']}")
    print(f"Delegation Files  : >{config['delegation_files']}")
    print(f"TELL Limit        : {config['tell_limit']} chars")
    print(f"Self-Critique     : {'Mandatory' if config['self_critique'] else 'Skip'}")
    print(f"DARRMS Focus      : {'Mandatory' if config['darrms_mandatory'] else 'Optional'}")
    print("============================================================")

def get_tier_banner(current_iteration: int = 0) -> str:
    """Return a one-line tier banner for orchestrator outputs."""
    config = get_tier_config()
    tier = config["tier"]
    max_iter = config["max_iterations"]
    darrms = "mandatory" if config["darrms_mandatory"] else "optional"
    return f"[TIER: {tier} | iter {current_iteration}/{max_iter} | DARRMS: {darrms}]"
