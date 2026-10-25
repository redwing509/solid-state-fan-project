"""Peer-review verification suite (ACCEPTANCE_CRITERIA.md section A). One pytest test per case."""
import pytest

from thermal1d import verification as V


@pytest.mark.parametrize("case", V.ALL, ids=[f.__name__ for f in V.ALL])
def test_case(case):
    checks = case()
    assert checks, "case produced no checks"
    failed = [c for c in checks if not c["passed"]]
    assert not failed, failed
