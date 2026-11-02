"""
Tests for languages parsed with tree-sitter (everything except Python).
The first run downloads each language's grammar, so it needs internet.
"""
import pytest

from backend.parser import parse_code


def outline(symbols):
    """Turns symbols into a short nested list like [("class", "Bank", [("method", "deposit", [])])]."""
    return [(s["type"], s["name"], outline(s["children"])) for s in symbols]


def parse(code, filename):
    result = parse_code(code, filename)
    assert result["error"] is None, result["error"]
    return outline(result["symbols"])


def test_javascript_classes_functions_and_arrow_functions():
    code = """export default function App() {
  const onClick = () => {}
  return <div onClick={onClick} />
}
const Button = ({ label }) => <button>{label}</button>
class Old extends React.Component {
  handle = () => {}
  render() { return null }
}
"""
    assert parse(code, "App.jsx") == [
        ("function", "App", [("function", "onClick", [])]),
        ("function", "Button", []),
        ("class", "Old", [("method", "handle", []), ("method", "render", [])]),
    ]


def test_typescript_interfaces_enums_and_class_fields():
    code = """interface Shape { area(): number }
export class Circle implements Shape {
  area(): number { return 1 }
  private handle = () => {}
}
type Id = string
enum Color { Red }
"""
    assert parse(code, "shape.ts") == [
        ("class", "Shape", [("method", "area", [])]),
        ("class", "Circle", [("method", "area", []), ("method", "handle", [])]),
        ("class", "Color", []),
    ]
    assert parse("export function App(): JSX.Element {\n  return <div />\n}\n", "App.tsx") == [
        ("function", "App", []),
    ]


def test_java_includes_annotations_and_constructors():
    code = """@Entity
public class Bank {
  public Bank() {}
  void deposit(int a) {}
  enum Kind { A, B }
}
"""
    result = parse_code(code, "Bank.java")
    assert outline(result["symbols"]) == [
        ("class", "Bank", [("method", "Bank", []), ("method", "deposit", []), ("class", "Kind", [])]),
    ]
    bank = result["symbols"][0]
    # Starts at the @Entity line so it shows up with the code
    assert (bank["line_start"], bank["line_end"]) == (1, 6)


def test_go_structs_and_methods_with_receivers():
    code = """package main
type Server struct { port int }
type ID string
func (s *Server) Start() error {
  return nil
}
func main() {}
"""
    result = parse_code(code, "server.go")
    assert outline(result["symbols"]) == [
        ("class", "Server", []),
        ("method", "Server.Start", []),
        ("function", "main", []),
    ]
    start = result["symbols"][1]
    assert (start["line_start"], start["line_end"]) == (4, 6)


def test_rust_impl_blocks_and_traits():
    code = """struct Point { x: i32 }
impl Point {
  fn new() -> Self { Point { x: 0 } }
}
impl Shape for Point {
  fn area(&self) -> f64 { 0.0 }
}
fn main() {}
"""
    assert parse(code, "lib.rs") == [
        ("class", "Point", []),
        ("class", "impl Point", [("method", "new", [])]),
        ("class", "impl Shape for Point", [("method", "area", [])]),
        ("function", "main", []),
    ]


def test_c_and_cpp_names_hidden_in_declarators():
    cpp = """namespace app {
class Bank {
  void deposit(int a) {}
};
}
void Bank::withdraw(int a) {}
int *make() { return 0; }
struct P p;
"""
    assert parse(cpp, "bank.cpp") == [
        ("class", "Bank", [("method", "deposit", [])]),
        ("function", "Bank::withdraw", []),
        ("function", "make", []),
    ]
    assert parse("struct point { int x; };\nint main(void) { return 0; }\n", "main.c") == [
        ("class", "point", []),
        ("function", "main", []),
    ]


@pytest.mark.parametrize("filename, code, expected", [
    ("Bank.cs", "namespace App {\n  public class Bank {\n    public void Deposit(int a) {}\n  }\n}\n",
     [("class", "Bank", [("method", "Deposit", [])])]),
    ("bank.rb", "module Banking\n  class Account\n    def deposit(a)\n    end\n  end\nend\n",
     [("class", "Banking", [("class", "Account", [("method", "deposit", [])])])]),
    ("bank.php", "<?php\nclass Bank {\n  public function deposit($a) {}\n}\nfunction helper() {}\n",
     [("class", "Bank", [("method", "deposit", [])]), ("function", "helper", [])]),
    ("Bank.kt", "class Bank {\n  fun deposit(a: Int) {}\n}\nobject Registry { fun get() {} }\n",
     [("class", "Bank", [("method", "deposit", [])]), ("class", "Registry", [("method", "get", [])])]),
    ("Bank.swift", "class Bank {\n  init() {}\n  func deposit(a: Int) {}\n}\nfunc main() {}\n",
     [("class", "Bank", [("method", "init", []), ("method", "deposit", [])]), ("function", "main", [])]),
    ("Main.scala", "object Main {\n  def main(args: Array[String]): Unit = {}\n}\n",
     [("class", "Main", [("method", "main", [])])]),
    ("bank.lua", "local function helper() end\nfunction Bank.deposit(self, a) end\n",
     [("function", "helper", []), ("function", "Bank.deposit", [])]),
])
def test_other_languages(filename, code, expected):
    assert parse(code, filename) == expected


def test_syntax_errors_still_return_what_was_found():
    result = parse_code("function ok() {}\nfunction broken( {\n", "broken.js")
    assert result["language"] == "javascript"
    assert outline(result["symbols"])[0] == ("function", "ok", [])
    assert "line 2" in result["error"]
