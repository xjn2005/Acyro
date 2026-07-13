from importlib.util import find_spec


def test_public_package_is_acyro() -> None:
    assert find_spec("acyro") is not None
    assert find_spec("forge") is None
