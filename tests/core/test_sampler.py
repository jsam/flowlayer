import uuid

import pytest

from datagears.core.api import FeatureStoreAPI
from datagears.core.network import Network
from datagears.core.sampler import Sampler


class TestSampler:
    def test_sampler_one_feature(self, store_feature: Network, feature_store: FeatureStoreAPI) -> None:
        """Test network run to store."""
        store_feature._version = f"0.1.1-{uuid.uuid4().hex}"  # type: ignore

        sample_one = store_feature.run(a=3, b=3, c1=10)
        assert sample_one.results

        samples = Sampler(store_feature).build().as_numpy
        assert samples.shape == (1, 1, 2)

        sample_two = store_feature.run(a=2, b=10, c1=50)
        assert sample_two.results

        samples = Sampler(store_feature).build().as_numpy
        assert samples.shape == (1, 2, 2)

        sample_three = store_feature.run(a=30, b=15, c1=55)
        assert sample_three.results

        samples = Sampler(store_feature).build().as_numpy
        assert samples.shape == (1, 3, 2)

        store_feature._version = f"0.1.2-{uuid.uuid4().hex}"  # type: ignore
        sample_one = store_feature.run(a=4, b=10, c1=30)
        assert sample_one.results

        samples = Sampler(store_feature, feature_store=feature_store).build().as_numpy
        assert samples.shape == (1, 1, 2)

    def test_sampler_offset(self, store_feature: Network) -> None:
        """Test sampler with offset."""

        another_feature = store_feature.copy(name=f"another_feature-{uuid.uuid4()}")

        one = another_feature.run(a=3, b=10, c1=35)
        assert one.identifier == another_feature.identifier
        two = another_feature.run(a=5, b=20, c1=35)
        assert two.identifier == another_feature.identifier

        samples = Sampler(another_feature, offset=1).build().as_numpy
        assert samples.shape == (1, 1, 2)

    def test_sampler_feature_aggregate(self, store_feature: Network) -> None:
        """Test feature aggregation."""
        store_feature.run(a=2, b=10, c1=55)
        store_feature.run(a=3, b=15, c1=45)

        another_feature = store_feature.copy(name="another_feature")

        one = another_feature.run(a=3, b=10, c1=35)
        assert one.identifier == another_feature.identifier
        two = another_feature.run(a=5, b=20, c1=35)
        assert two.identifier == another_feature.identifier

        samples = Sampler(store_feature, another_feature).build().as_numpy
        assert samples.shape == (2,)

    def test_sampler_exceptions(self, store_feature: Network) -> None:
        """Test sampler raising of exceptions."""
        with pytest.raises(ValueError) as exp:
            Sampler(store_feature).as_numpy

        assert str(exp.value) == "object is not built - invoke .build() before access"
