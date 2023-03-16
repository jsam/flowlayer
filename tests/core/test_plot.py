from pathlib import Path

import pytest

from datagears.core.api import NetworkPlotAPI
from datagears.core.network import Network


def test_network_plot(myfeature: Network) -> None:
    """Test network plot."""
    plot: NetworkPlotAPI = myfeature.plot

    assert plot.show is None

    plot.to_file("out_test.png")
    assert Path("out_test.png").exists()

    with pytest.raises(ValueError):
        plot.to_file(None)  # type: ignore
