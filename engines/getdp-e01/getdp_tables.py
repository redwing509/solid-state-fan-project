"""Parse GetDP table lines and Gmsh mesh_info without backtracking regex."""
from __future__ import annotations


def floats_in(line: str):
    """Split a line on whitespace and keep tokens that parse as floats."""
    out = []
    for tok in line.split():
        try:
            out.append(float(tok))
        except ValueError:
            continue
    return out


def node_count(text: str):
    """Return the first integer that immediately precedes the word 'nodes'."""
    tokens = text.split()
    for tok, nxt in zip(tokens, tokens[1:]):
        if nxt == "nodes":
            try:
                return int(tok)
            except ValueError:
                continue
    return None
