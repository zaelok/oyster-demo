import pytest

from oyster.graph import upstream_of, validate_path
from oyster.graph.catalog import CATALOG, PATH_B, PATH_C
from oyster.types import Edge, Node, Path

ALIASES = {"cheap-model", "strong-model"}


def node(node_id: str, role: str = "deep-reviewer", alias: str = "strong-model") -> Node:
    return Node(node_id, role, alias, "deep_reviewer")


def path(nodes, edges=()):
    return Path("T", "test", tuple(nodes), tuple(edges))


def test_rule_1_duplicate_node_ids():
    with pytest.raises(ValueError, match="duplicate node id 'x'"):
        validate_path(path([node("x"), node("x")]), ALIASES)


def test_rule_2_edge_endpoint_must_exist():
    with pytest.raises(ValueError, match="unknown node id 'zz'"):
        validate_path(path([node("a"), node("b")], [Edge("a", "zz")]), ALIASES)


def test_rule_3_no_cycles():
    with pytest.raises(ValueError, match="cycle through"):
        validate_path(path([node("a"), node("b")], [Edge("a", "b"), Edge("b", "a")]), ALIASES)


def test_rule_3_self_loop_is_a_cycle():
    with pytest.raises(ValueError, match="cycle through a -> a"):
        validate_path(path([node("a")], [Edge("a", "a")]), ALIASES)


def test_rule_4_nodes_must_be_topologically_ordered():
    with pytest.raises(ValueError, match="not in topological order"):
        validate_path(path([node("b"), node("a")], [Edge("a", "b")]), ALIASES)


def test_rule_5_model_alias_must_be_known():
    with pytest.raises(ValueError, match="unknown model alias 'gpt'"):
        validate_path(path([node("a", alias="gpt")]), ALIASES)


def test_rule_6_prompt_key_must_be_in_templates():
    bad = Node("a", "deep-reviewer", "strong-model", "no_such_prompt")
    with pytest.raises(ValueError, match="unknown prompt key 'no_such_prompt'"):
        validate_path(path([bad]), ALIASES)


def test_rule_7_roles_may_repeat_but_ids_may_not():
    repeated = path([node("a"), node("b")], [Edge("a", "b")])
    validate_path(repeated, ALIASES)
    with pytest.raises(ValueError, match="duplicate node id"):
        validate_path(path([node("a"), node("a")], [Edge("a", "a")]), ALIASES)


def test_every_catalog_path_validates():
    for catalog_path in CATALOG:
        validate_path(catalog_path, ALIASES)


def test_path_c_validates_despite_repeated_role():
    roles = [n.role for n in PATH_C.nodes]
    assert roles == ["deep-reviewer", "critic", "deep-reviewer"]
    assert [n.id for n in PATH_C.nodes] == ["c1", "c2", "c3"]
    assert len(PATH_C.edges) == 2
    validate_path(PATH_C, ALIASES)


def test_catalog_shape_matches_spec():
    assert [p.id for p in CATALOG] == ["A", "B", "C"]
    assert len(CATALOG[0].nodes) == 1 and CATALOG[0].edges == ()
    assert len(PATH_B.nodes) == 2 and len(PATH_B.edges) == 1
    assert CATALOG[0].nodes[0].role == "cheap-scanner"
    assert CATALOG[0].nodes[0].model_alias == "cheap-model"


def test_upstream_of_returns_sources_in_path_order():
    fan_in = path([node("a"), node("b"), node("c")], [Edge("b", "c"), Edge("a", "c")])
    validate_path(fan_in, ALIASES)
    assert upstream_of(fan_in, "c") == ("a", "b")
    assert upstream_of(fan_in, "a") == ()
    assert upstream_of(PATH_C, "c3") == ("c2",)
