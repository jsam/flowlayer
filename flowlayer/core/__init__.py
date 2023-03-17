"""
from datagears import engine, Gear

# Init
engine.init({
    redis_uri: "redis://myuser:mypassword@localhost:6379"
})

# Functional interface
add_op = Gear(name="add_op")(add)
reduce_op = Gear(name="reduce_op", Depends(add_op), Params({"c": 3}))(reduce)
output = Gear(name="output", Depends(reduce_op), Params({"d": 5}))(final_calc)

add_op(2, 3) == add(2, 3)
True


# Seemless interface


def add(a, b: int) -> int:
    return a + b

def reduce(b: int = Depends(add), c: int) -> int:
    return b - c

def final_calc(a: int = Depends(reduce), d: int) -> int:
    return a + d


my_graph = dg.Network(name="my_network", outputs=[final_calc, reduce])
my_graph.plot()
my_graph.run(a=5, b=3, c=4, d=6)
my_graph.register()


# Network
my_graph = Network(name="my_awesome_network", output)

my_graph.plot()
[matplotlib.plot]


my_graph.run({"a": 1, "b:" 2, "c": 3, "d": 4}, blocking=True)
4

my_graph.register()

# In some other process (e.g. workers) we could do the following.
networks = engine.get_networks()
[Network("my_awesome_network")]

networks[0].run({"a": 1, "b:" 2, "c": 3, "d": 5}, blocking=True)
5

"""
