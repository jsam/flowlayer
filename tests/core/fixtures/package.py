import shutil
from pathlib import Path
from typing import Iterator

import pytest
from filelock import FileLock


@pytest.fixture(scope="session")
def egg_path() -> Iterator[Path]:
    """Create an egg package."""
    from datagears.core.package import Package

    lck = FileLock("egg_fixture.lock")
    lck.acquire()

    package = Package()

    # NOTE: Build a package.
    egg_path = package.make_egg()
    assert egg_path.exists()

    # NOTE: Prepare duplicate for checking of multiple eggs.
    dst = Path("".join([*str(egg_path).split(".egg"), "_copy", ".egg"]))
    shutil.copyfile(egg_path, dst)
    assert dst.exists()

    # NOTE: Test rebuilding of dist directory, correct raise of exception.
    package._dist_dir.mkdir(exist_ok=True)  # type: ignore
    _rmtree = shutil.rmtree
    shutil.rmtree = lambda x: x  # type: ignore
    with pytest.raises(ValueError) as exp:
        package.make_egg()
    shutil.rmtree = _rmtree

    assert str(exp.value) == "multiple eggs found"

    # NOTE: Check correct exception raised in case of no setup.py file.
    _cwd = package._cwd  # type: ignore
    package._cwd = None  # type: ignore
    with pytest.raises(ValueError) as exp:
        package.make_egg()

    assert str(exp.value) == "cannot find setup.py"
    package._cwd = _cwd  # type: ignore

    # NOTE: Change the egg building command and check if correct exception is raised when no eggs are found.
    Package.BUILD_EGG_CMD = "python setup.py sdist"  # type: ignore
    with pytest.raises(ValueError) as exp:
        package.make_egg()

    assert str(exp.value) == "egg was not built"

    # NOTE: Wipe everything and build an egg as expected.
    shutil.rmtree("dist")
    Package.BUILD_EGG_CMD = "python setup.py bdist_egg"  # type: ignore

    yield Package().make_egg()

    lck.release()
