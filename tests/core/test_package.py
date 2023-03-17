import os
from pathlib import Path

import pytest

from flowlayer.core.package import Package, chdir


class TestPackage:
    """Tests for packager."""

    def test_setup_name(self) -> None:
        """Check constant name."""
        assert Package.SETUP_NAME == "setup.py"

    def test_children(self) -> None:
        """Check children results."""
        children = Package.children(Path("."))
        assert Package.SETUP_NAME in children

        with pytest.raises(ValueError):
            Package.children(Path("setup.py"))

        assert Package.children(Path("/tmp/doesnotexist")) == []

    def test_package_constructor(self) -> None:
        """Check package construction."""
        _cwd = Path(os.getcwd())
        package = Package()
        assert package.root == _cwd

        os.chdir("flowlayer/core")
        package_child = Package()
        assert package_child.root == _cwd

        os.chdir(f"{_cwd}/..")
        with pytest.raises(ValueError):
            Package()

        os.chdir(_cwd)

    def test_package_chdir(self) -> None:
        """Test chdir context manager."""
        _cwd = Path(os.getcwd())

        with chdir("flowlayer/core"):
            assert Path(os.getcwd()) == _cwd / "flowlayer" / "core"

        assert Path(os.getcwd()) == _cwd

    def test_make_egg_exceptions(self, egg_path: Path) -> None:
        """Test make egg exceptions."""
        package = egg_path
        assert package.exists() is True
