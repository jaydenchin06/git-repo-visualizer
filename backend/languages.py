"""
Finds classes, functions and methods in languages other than Python.

It uses tree-sitter, the same kind of parser GitHub and most code editors use.
tree-sitter turns code into a tree of "nodes" (like class_declaration or
function_definition), and the RULES table below says which of those nodes count
as a class or a function in each language. Everything else is shared, so adding
a language is usually just one entry in LANGUAGES and one in RULES.

Each language's grammar is downloaded the first time it's needed (about 1-2 MB)
and cached after that, so the first file in a new language needs internet.
"""
import threading
from typing import Dict, List, Optional

try:
    from tree_sitter import Parser
    from tree_sitter_language_pack import get_language as load_grammar
except ImportError:
    # The backend still works without it, it just can only parse Python
    Parser = None


# File extension -> (language name, tree-sitter grammar).
# The language name is what highlight.js uses to colour the code in the frontend.
LANGUAGES = {
    ".js": ("javascript", "javascript"), ".jsx": ("javascript", "javascript"),
    ".mjs": ("javascript", "javascript"), ".cjs": ("javascript", "javascript"),
    ".ts": ("typescript", "typescript"), ".mts": ("typescript", "typescript"),
    ".cts": ("typescript", "typescript"), ".tsx": ("typescript", "tsx"),
    ".java": ("java", "java"),
    ".c": ("c", "c"), ".h": ("c", "cpp"),  # .h files are often C++, which is (almost) a superset of C
    ".cpp": ("cpp", "cpp"), ".cc": ("cpp", "cpp"), ".cxx": ("cpp", "cpp"),
    ".hpp": ("cpp", "cpp"), ".hh": ("cpp", "cpp"), ".hxx": ("cpp", "cpp"),
    ".cs": ("csharp", "csharp"),
    ".go": ("go", "go"),
    ".rs": ("rust", "rust"),
    ".rb": ("ruby", "ruby"),
    ".php": ("php", "php"),
    ".kt": ("kotlin", "kotlin"), ".kts": ("kotlin", "kotlin"),
    ".swift": ("swift", "swift"),
    ".scala": ("scala", "scala"),
    ".lua": ("lua", "lua"),
}

_JAVASCRIPT_RULES = {
    "class": {"class_declaration", "class"},
    "function": {"function_declaration", "generator_function_declaration", "method_definition"},
    # const handleClick = () => {...} and class fields like onClick = () => {...}
    "assigned": {"variable_declarator", "field_definition"},
}
_TYPESCRIPT_RULES = {
    "class": {"class_declaration", "abstract_class_declaration", "class", "interface_declaration", "enum_declaration"},
    "function": {"function_declaration", "generator_function_declaration", "method_definition",
                 "method_signature", "abstract_method_signature"},
    "assigned": {"variable_declarator", "public_field_definition"},
}

# Grammar -> which node types are classes and which are functions.
# Things like structs, interfaces and traits count as classes, since they hold methods.
# A function directly inside a class is shown as a method.
RULES = {
    "javascript": _JAVASCRIPT_RULES,
    "typescript": _TYPESCRIPT_RULES,
    "tsx": _TYPESCRIPT_RULES,
    "java": {
        "class": {"class_declaration", "interface_declaration", "enum_declaration", "record_declaration",
                  "annotation_type_declaration"},
        "function": {"method_declaration", "constructor_declaration"},
    },
    "c": {
        "class": {"struct_specifier", "union_specifier", "enum_specifier"},
        "function": {"function_definition"},
    },
    "cpp": {
        "class": {"class_specifier", "struct_specifier", "union_specifier", "enum_specifier"},
        "function": {"function_definition"},
    },
    "csharp": {
        "class": {"class_declaration", "struct_declaration", "interface_declaration", "record_declaration",
                  "enum_declaration"},
        "function": {"method_declaration", "constructor_declaration", "local_function_statement"},
    },
    "go": {
        "class": {"type_spec"},  # only structs and interfaces, see _symbol_type
        "function": {"function_declaration", "method_declaration"},
    },
    "rust": {
        "class": {"struct_item", "enum_item", "union_item", "trait_item", "impl_item"},
        "function": {"function_item", "function_signature_item"},
    },
    "ruby": {
        "class": {"class", "module"},
        "function": {"method", "singleton_method"},
    },
    "php": {
        "class": {"class_declaration", "interface_declaration", "trait_declaration", "enum_declaration"},
        "function": {"function_definition", "method_declaration"},
    },
    "kotlin": {
        "class": {"class_declaration", "object_declaration"},
        "function": {"function_declaration"},
    },
    "swift": {
        "class": {"class_declaration", "protocol_declaration"},
        "function": {"function_declaration", "protocol_function_declaration", "init_declaration"},
    },
    "scala": {
        "class": {"class_definition", "object_definition", "trait_definition"},
        "function": {"function_definition", "function_declaration"},
    },
    "lua": {
        "class": set(),
        "function": {"function_declaration"},
    },
}

# Values that make an "assigned" node (like const x = ...) a function
_FUNCTION_VALUES = {"arrow_function", "function_expression", "function", "generator_function"}
# Node types that hold a name when a definition has no "name" field (e.g. Kotlin)
_NAME_TYPES = {"identifier", "type_identifier", "simple_identifier", "field_identifier",
               "property_identifier", "constant", "name", "qualified_identifier",
               "destructor_name", "operator_name"}

_grammars = {}
_grammars_lock = threading.Lock()


def get_language_info(extension: str) -> Optional[tuple]:
    """Returns (language name, grammar) for a file extension, or None if we can't parse it."""
    return LANGUAGES.get(extension)


def parse_with_tree_sitter(code: str, grammar: str) -> Dict:
    """
    Parses code in any language from RULES.

    Args:
        code: The file contents
        grammar: A tree-sitter grammar name from LANGUAGES (e.g. "javascript")

    Returns:
        A dictionary with symbols (same shape as parse_python in parser.py) and
        error (a message if part of the file couldn't be parsed, else None).
        tree-sitter keeps going past mistakes, so there can be symbols and an error.
    """
    if Parser is None:
        return {"symbols": [], "error": "tree-sitter isn't installed (or couldn't load), so only Python can be "
                                        "parsed. Run: pip install -r backend/requirements.txt"}

    try:
        parser = Parser(_get_grammar(grammar))
    except Exception:
        return {"symbols": [], "error": f"Couldn't download the {grammar} parser. It's downloaded the first "
                                        "time it's needed, so check your internet connection."}

    tree = parser.parse(code.encode("utf-8"))
    try:
        symbols = _find_symbols(tree.root_node, RULES[grammar], inside_class=False)
    except RecursionError:
        return {"symbols": [], "error": "This file is nested too deeply to read."}

    error = None
    if tree.root_node.has_error:
        error = f"Couldn't fully read this file around line {_first_error_line(tree.root_node)}. It may have a syntax error."
    return {"symbols": symbols, "error": error}


def _get_grammar(grammar: str):
    """Loads a grammar once and reuses it (loading can mean downloading it)."""
    with _grammars_lock:
        if grammar not in _grammars:
            _grammars[grammar] = load_grammar(grammar)
        return _grammars[grammar]


def _find_symbols(node, rules: Dict, inside_class: bool) -> List[Dict]:
    """
    Looks through a node's children for classes and functions. Anything else
    (namespaces, export statements, class bodies...) is searched through, so
    symbols are found however deeply they're wrapped.
    """
    symbols = []
    for child in node.named_children:
        symbol_type = _symbol_type(child, rules)
        name = _symbol_name(child) if symbol_type else None
        if not name:
            symbols.extend(_find_symbols(child, rules, inside_class))
            continue

        # Go methods are written outside the struct but still belong to it
        if symbol_type == "function" and (inside_class or child.child_by_field_name("receiver")):
            symbol_type = "method"

        symbols.append({
            "name": name,
            "type": symbol_type,
            "line_start": child.start_point.row + 1,
            "line_end": _last_line(child),
            "children": _find_symbols(child, rules, inside_class=(symbol_type == "class")),
        })
    return symbols


def _symbol_type(node, rules: Dict) -> Optional[str]:
    """Returns "class" or "function" if this node defines one, else None."""
    if node.type in rules["class"]:
        # struct point p; uses a struct without defining it, so only count ones with a body
        if node.type.endswith("_specifier") and node.child_by_field_name("body") is None:
            return None
        # In Go, type_spec is any named type (type ID string), so only keep structs and interfaces
        if node.type == "type_spec":
            kind = node.child_by_field_name("type")
            return "class" if kind is not None and kind.type in ("struct_type", "interface_type") else None
        return "class"
    if node.type in rules["function"]:
        return "function"
    if node.type in rules.get("assigned", ()):
        value = node.child_by_field_name("value")
        if value is not None and value.type in _FUNCTION_VALUES:
            return "function"
    return None


def _symbol_name(node) -> Optional[str]:
    """Works out the name of a class or function node, or None if it has no name."""
    if node.type == "impl_item":
        # Rust: impl Point { ... } or impl Shape for Point { ... }
        trait, target = node.child_by_field_name("trait"), node.child_by_field_name("type")
        if target is None:
            return None
        return f"impl {_text(trait)} for {_text(target)}" if trait else f"impl {_text(target)}"

    name_node = (node.child_by_field_name("name")
                 or node.child_by_field_name("property")  # JavaScript class fields
                 or _declarator_name(node)                # C and C++
                 or next((c for c in node.named_children if c.type in _NAME_TYPES), None))
    if name_node is None:
        return None
    name = _text(name_node)

    receiver = node.child_by_field_name("receiver")
    if receiver is not None:
        # Go: func (s *Server) Start() -> Server.Start
        receiver_type = _text(receiver).strip("()").split()[-1].lstrip("*")
        name = f"{receiver_type}.{name}"
    return name


def _declarator_name(node):
    """
    C and C++ hide a function's name inside "declarators", e.g.
    int *Bank::total(int x) is pointer_declarator -> function_declarator -> Bank::total
    """
    declarator = node.child_by_field_name("declarator")
    while declarator is not None:
        if declarator.type in _NAME_TYPES:
            return declarator
        declarator = declarator.child_by_field_name("declarator") or next(iter(declarator.named_children), None)
    return None


def _text(node) -> str:
    # Squash spaces/newlines so long names (like generics) stay on one line
    return " ".join(node.text.decode("utf-8", errors="replace").split())[:120]


def _last_line(node) -> int:
    """The last line of a node (some grammars end a node at the start of the next line)."""
    row, column = node.end_point.row, node.end_point.column
    if column == 0 and row > node.start_point.row:
        row -= 1
    return row + 1


def _first_error_line(node) -> int:
    """Follows the parts of the tree that contain errors down to the first one."""
    while node.type != "ERROR" and not node.is_missing:
        broken = next((c for c in node.children if c.has_error or c.is_missing), None)
        if broken is None:
            break
        node = broken
    return node.start_point.row + 1
