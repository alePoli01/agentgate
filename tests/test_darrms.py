"""
Tests for darrms.py
"""
import sys
import os
import unittest
import tempfile
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
import darrms

class TestDARRMS(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmpdir.cleanup()

    def _write_temp(self, name, content):
        path = os.path.join(self.tmpdir.name, name)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        return path

    @patch("darrms.safe_append")
    def test_collapse_python(self, mock_append):
        code = '''import os
from pathlib import Path

def helper():
    print("helper")
    return True

class MyClass:
    def __init__(self):
        self.x = 1
        
    def do_work(self):
        print("work")
        
@decorator
def decorated():
    pass
'''
        path = self._write_temp("test.py", code)
        result = darrms.collapse_file_darrrms(path)
        
        self.assertIn("import os", result)
        self.assertIn("from pathlib import Path", result)
        self.assertIn("def helper():", result)
        self.assertIn("class MyClass:", result)
        self.assertIn("def __init__(self):", result)
        self.assertIn("def do_work(self):", result)
        self.assertIn("@decorator", result)
        self.assertIn("def decorated():", result)
        self.assertNotIn('print("helper")', result)
        
        # Verify FOCUSED_FILES_PATH was appended to
        mock_append.assert_called_once()
        self.assertIn("test.py", mock_append.call_args[0][1])

    @patch("darrms.safe_append")
    def test_collapse_js_ts(self, mock_append):
        code = '''import { something } from 'lib';
const helper = () => {
    console.log(1);
}
function normalFunc(a, b) {
    return a + b;
}
class JSClass {
    constructor() {
        this.a = 1;
    }
    method() {
        return true;
    }
}
export const exportedArrow = () => 1;
'''
        path = self._write_temp("test.ts", code)
        result = darrms.collapse_file_darrrms(path)
        
        self.assertIn("import { something } from 'lib';", result)
        self.assertIn("const helper = () => {", result)
        self.assertIn("function normalFunc(a, b) {", result)
        self.assertIn("class JSClass {", result)
        self.assertNotIn("console.log(1);", result)
        
    @patch("darrms.safe_append")
    def test_collapse_go(self, mock_append):
        code = '''package main
import "fmt"
func main() {
    fmt.Println("hello")
}
type MyStruct struct {
    x int
}
'''
        path = self._write_temp("test.go", code)
        result = darrms.collapse_file_darrrms(path)
        
        self.assertIn("package main", result)
        self.assertIn('import "fmt"', result)
        self.assertIn("func main() {", result)
        self.assertIn("type MyStruct struct {", result)
        self.assertNotIn("fmt.Println", result)

    @patch("darrms.safe_append")
    def test_collapse_rust(self, mock_append):
        code = '''use std::io;
fn main() {
    println!("hello");
}
impl MyStruct {
    fn helper() {}
}
pub struct AnotherStruct {
    x: i32
}
'''
        path = self._write_temp("test.rs", code)
        result = darrms.collapse_file_darrrms(path)
        
        self.assertIn("use std::io;", result)
        self.assertIn("fn main() {", result)
        self.assertIn("impl MyStruct {", result)
        self.assertIn("pub struct AnotherStruct {", result)
        self.assertNotIn("println!", result)
        
    @patch("darrms.safe_append")
    def test_unknown_extension_fallback(self, mock_append):
        code = "line1\nline2\nline3\n"
        path = self._write_temp("test.unknown", code)
        result = darrms.collapse_file_darrrms(path)
        self.assertIn("[DARRMS FALLBACK", result)
        self.assertIn("line1", result)

if __name__ == "__main__":
    unittest.main()
