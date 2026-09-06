"""The three shipped paths as data (architecture §2.2). Adding a strategy means adding a Path
here; selection, execution and measurement code do not change."""

from oyster.types import Edge, Node, Path

PATH_A = Path(
    id="A",
    description="single cheap pass: cheap-scanner(cheap-model)",
    nodes=(Node("a1", "cheap-scanner", "cheap-model", "cheap_scanner"),),
    edges=(),
)

PATH_B = Path(
    id="B",
    description="cascade: cheap-scanner(cheap-model) -> deep-reviewer(strong-model)",
    nodes=(
        Node("b1", "cheap-scanner", "cheap-model", "cheap_scanner"),
        Node("b2", "deep-reviewer", "strong-model", "deep_reviewer"),
    ),
    edges=(Edge("b1", "b2"),),
)

PATH_C = Path(
    id="C",
    description="bounded iteration: deep-reviewer -> critic -> deep-reviewer (strong-model)",
    nodes=(
        Node("c1", "deep-reviewer", "strong-model", "deep_reviewer"),
        Node("c2", "critic", "strong-model", "critic"),
        Node("c3", "deep-reviewer", "strong-model", "deep_reviewer"),
    ),
    edges=(Edge("c1", "c2"), Edge("c2", "c3")),
)

CATALOG: tuple[Path, ...] = (PATH_A, PATH_B, PATH_C)
