from typing import Dict, List

from backend.parser import parse_code


def build_tree(files: Dict[str, str], root_name: str) -> Dict:
    """
    Builds the full hierarchy (folders -> files -> classes -> methods) for a set of files.

    Args:
        files: A dictionary mapping each file path (like "src/app.py") to its contents
        root_name: The name to show for the top folder (like the repo name)

    Returns:
        The root folder node. Every node has: id, name, type and children.
        File nodes also have path, language, line_count and error.
        Symbol nodes (class/function/method) also have path, line_start and line_end,
        so the frontend can cut their code out of the file contents.
    """
    root = {"id": "", "name": root_name, "type": "folder", "path": "", "children": []}

    for path in sorted(files):
        parts = path.split("/")

        # Walk down the folders in the path, creating any that don't exist yet
        folder = root
        for i, part in enumerate(parts[:-1]):
            folder_path = "/".join(parts[: i + 1])
            existing = next((c for c in folder["children"] if c["type"] == "folder" and c["name"] == part), None)
            if existing is None:
                existing = {"id": folder_path, "name": part, "type": "folder", "path": folder_path, "children": []}
                folder["children"].append(existing)
            folder = existing

        content = files[path]
        parsed = parse_code(content, parts[-1])
        folder["children"].append({
            "id": path,
            "name": parts[-1],
            "type": "file",
            "path": path,
            "language": parsed["language"],
            "line_count": len(content.split("\n")),
            "error": parsed["error"],
            "children": _symbol_nodes(parsed["symbols"], path, parent_id=path),
        })

    _sort_folders(root)
    return root


def _symbol_nodes(symbols: List[Dict], path: str, parent_id: str) -> List[Dict]:
    """Adds an id and the file path to each symbol so the frontend can find its code."""
    nodes = []
    for symbol in symbols:
        # Include the line number in case two symbols share a name
        node_id = f"{parent_id}::{symbol['name']}@{symbol['line_start']}"
        nodes.append({
            "id": node_id,
            "name": symbol["name"],
            "type": symbol["type"],
            "path": path,
            "line_start": symbol["line_start"],
            "line_end": symbol["line_end"],
            "children": _symbol_nodes(symbol["children"], path, parent_id=node_id),
        })
    return nodes


def _sort_folders(folder: Dict) -> None:
    """Sorts a folder's children (folders first, then files, alphabetically), recursively."""
    folder["children"].sort(key=lambda c: (c["type"] != "folder", c["name"].lower()))
    for child in folder["children"]:
        if child["type"] == "folder":
            _sort_folders(child)
