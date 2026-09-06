"""Path validation. Paths are data: the selector, executor and evaluation operate on the same
tuple of nodes and edges, which is what lets one algorithm rank every strategy
(architecture §1.5)."""

from oyster.prompts.templates import TEMPLATES
from oyster.types import Path

__all__ = ["upstream_of", "validate_path"]


def validate_path(path: Path, known_aliases: set[str]) -> None:
    """Raise ValueError with a specific message on the first violation, checked in rule order:
    unique ids, known edge endpoints, no cycles, topological node order, known model aliases,
    known prompt keys. Roles may repeat across nodes; only ids must be unique."""
    seen: set[str] = set()
    for node in path.nodes:
        if node.id in seen:
            raise ValueError(f"path {path.id!r}: duplicate node id {node.id!r}")
        seen.add(node.id)

    for edge in path.edges:
        for endpoint in (edge.src, edge.dst):
            if endpoint not in seen:
                raise ValueError(
                    f"path {path.id!r}: edge {edge.src!r}->{edge.dst!r} "
                    f"references unknown node id {endpoint!r}"
                )

    cycle = _find_cycle(path)
    if cycle:
        raise ValueError(f"path {path.id!r}: cycle through {' -> '.join(cycle)}")

    position = {node.id: index for index, node in enumerate(path.nodes)}
    for edge in path.edges:
        if position[edge.src] >= position[edge.dst]:
            raise ValueError(
                f"path {path.id!r}: nodes are not in topological order, "
                f"edge {edge.src!r}->{edge.dst!r} points backwards"
            )

    for node in path.nodes:
        if node.model_alias not in known_aliases:
            raise ValueError(
                f"path {path.id!r}: node {node.id!r} uses unknown model alias {node.model_alias!r}"
            )

    for node in path.nodes:
        if node.prompt_key not in TEMPLATES:
            raise ValueError(
                f"path {path.id!r}: node {node.id!r} uses unknown prompt key {node.prompt_key!r}"
            )


def _find_cycle(path: Path) -> list[str]:
    """Return the node ids of one cycle (closed, first id repeated at the end) or []."""
    adjacency: dict[str, list[str]] = {node.id: [] for node in path.nodes}
    for edge in path.edges:
        adjacency[edge.src].append(edge.dst)

    white, grey, black = 0, 1, 2
    color = dict.fromkeys(adjacency, white)
    stack: list[str] = []

    def visit(node_id: str) -> list[str]:
        color[node_id] = grey
        stack.append(node_id)
        for nxt in adjacency[node_id]:
            if color[nxt] == grey:
                return stack[stack.index(nxt) :] + [nxt]
            if color[nxt] == white:
                found = visit(nxt)
                if found:
                    return found
        stack.pop()
        color[node_id] = black
        return []

    for node_id in adjacency:
        if color[node_id] == white:
            found = visit(node_id)
            if found:
                return found
    return []


def upstream_of(path: Path, node_id: str) -> tuple[str, ...]:
    """Node ids with an edge into node_id, in path order."""
    sources = {edge.src for edge in path.edges if edge.dst == node_id}
    return tuple(node.id for node in path.nodes if node.id in sources)
