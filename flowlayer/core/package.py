import contextlib
import os
import shutil
from pathlib import Path
from typing import Iterator, List, Optional, Union

from filelock import FileLock


@contextlib.contextmanager
def chdir(path: Union[Path, str]) -> Iterator[None]:
    """Change the current working directory."""
    cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(cwd)


class Package:
    """Create an egg package."""

    SETUP_NAME = "setup.py"
    BUILD_EGG_CMD = "python setup.py bdist_egg"

    def __init__(self, dist_dir: Path = Path("dist")) -> None:
        """Constructor for packager."""
        self._dist_dir = dist_dir
        self._cwd: Optional[Path] = Path(os.getcwd())

        _found = False
        while True:
            if Package.SETUP_NAME in self.children(self._cwd):
                _found = True
                break

            if self._cwd == self._cwd.parent:
                break

            self._cwd = self._cwd.parent

        if _found is False:
            self._cwd = None
            raise ValueError("package setup not found")

    @property
    def root(self) -> Optional[Path]:
        """Returns the root of the package."""
        return self._cwd

    @staticmethod
    def children(path: Path) -> List[str]:
        """ "Return children of a directory."""
        if path.exists() and not path.is_dir():
            raise ValueError

        if path.exists():
            return [_child.name for _child in path.iterdir()]

        return []

    def make_egg(self) -> Path:
        """Creates an egg."""
        if self._cwd is None:
            raise ValueError("cannot find setup.py")

        with chdir(self._cwd), FileLock(str(self._cwd / "egg.lock")):
            if self._dist_dir.exists():
                shutil.rmtree(self._dist_dir)

            os.system(Package.BUILD_EGG_CMD)

        _results: List[Path] = [Path(self._cwd / self._dist_dir / _child) for _child in self.children(self._dist_dir) if _child.endswith(".egg")]

        if len(_results) > 1:
            raise ValueError("multiple eggs found")

        if not _results:
            raise ValueError("egg was not built")

        return _results[0]
