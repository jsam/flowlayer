from typing import List, Tuple

from numpy import array, ndarray, random

from flowlayer.core.network import Network


class TestFeatureStore:
    def test_feature_store(self, myfeature: Network) -> None:
        """Test feature store get and set."""
        from flowlayer.core.stores import FeatureStore

        store = FeatureStore()

        tensor: ndarray = array([1, 2, 3])
        stream_id, key = store.set(tensor, myfeature)

        assert stream_id
        assert key
        assert len(key.split("-")) == 3

        assert all(store.get(key) == tensor)  # type: ignore

    def test_multiple_samples(self, myfeature: Network) -> None:
        """Test generation of multiple samples."""
        from flowlayer.core.stores import FeatureStore

        store = FeatureStore()

        expected: List[Tuple[str, str]] = [store.set(tensor, myfeature) for tensor in random.rand(100, 3)]

        start = expected[0][0]
        expected_keys = [item[1] for item in expected]

        received_keys: List[str] = [key[1] for key in store.get_keys(myfeature, start=start)]

        assert expected_keys == received_keys
