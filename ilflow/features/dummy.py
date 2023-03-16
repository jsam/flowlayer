from numpy import array, ndarray

from ilflow.core.network import Depends, Maybe


def add(a: int, b: int = 10) -> int:
    return a + b


def reduce(c1: int, sum: Maybe[int] = Depends(add)) -> int:
    result = sum - c1
    return result


def add_one() -> int:
    return 1


def my_out(reduced: Maybe[int] = Depends(reduce), add_one: Maybe[int] = Depends(add_one)) -> ndarray:
    result = [reduced, add_one]
    return array(result)
