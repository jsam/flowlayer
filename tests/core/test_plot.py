from pathlib import Path

import pytest

from flowlayer.core.api import NetworkPlotAPI
from flowlayer.core.network import Network


def test_network_plot(mynetwork: Network) -> None:
    """Test network plot."""
    plot: NetworkPlotAPI = mynetwork.plot

    assert plot.show is None

    plot.to_file("out_test.png")
    assert Path("out_test.png").exists()

    with pytest.raises(ValueError):
        plot.to_file(None)  # type: ignore
