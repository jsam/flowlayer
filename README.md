# flowlayer

[![image][]][1]

Lightweight data processing with typed workflows.

# Getting started

```python
from flowlayer import Depends, Flow


def add(a, b) -> int:
    return a + b


def reduce(c: int, sum: int = Depends(add)) -> int:
    return sum - c


def my_out(reduced: int = Depends(reduce)) -> float:
    return reduced / 2


my_graph = Flow(name="mynet", outputs=[my_out]) 
my_graph.plot.view()
```


Which should produce following computational graph:

<p align="center">
    <img src="assets/out.png" />
</p>


To inspect the `input_shape` we can check with:

```python
network.input_shape
> {'c': int, 'a': typing.Any, 'b': typing.Any}
```

To execute our newly composed computation, we can execute it with given parameters:
```python
my_graph.run(a=5, b=3, c=4, d=6)
```

# Remote Execution

## Using process pool
To register and deploy the graph to the cluster and execute it from other
processes, define the execution engine first:

```python
from flowlayer.core.engine import PoolEngine

with PoolEngine(max_workers=4) as engine:
    result = engine.run(my_graph, a=5, b=3, c=4)
```

### Using Ray

```python
from flowlayer.core.engine import RayEngine

with RayEngine(max_workers=4) as engine:
    result = engine.run(my_graph, a=5, b=3, c=4)
```



  [image]: https://badge.fury.io/py/flowlayer.png
  [1]: http://badge.fury.io/py/flowlayer
