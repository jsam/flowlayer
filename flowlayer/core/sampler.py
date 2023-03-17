# from typing import List, Optional, Tuple

# import numpy
# from ilflow.core.api import FeatureStoreAPI
# from ilflow.core.network import NetworkAPI
# from ilflow.core.stores import FeatureStore


# class Sampler:
#     """Retrieve samples for a given set of features."""

#     def __init__(self, *features: NetworkAPI, limit: int = 1000, offset: int = 0, feature_store: Optional[FeatureStoreAPI] = None) -> None:
#         """Sample constructor."""
#         self._features: List[NetworkAPI] = list(features)
#         self._limit = limit
#         self._offset = offset

#         if feature_store is None:
#             self._feature_store: FeatureStoreAPI = FeatureStore()
#         else:
#             self._feature_store = feature_store

#         self._data: Optional[numpy.ndarray] = None

#     @property
#     def as_numpy(self) -> numpy.ndarray:
#         """Materialize and aggregate all given features and return as a tensor."""
#         if self._data is None:
#             raise ValueError("object is not built - invoke .build() before access")

#         return self._data

#     def _sample_feature(self, feature: NetworkAPI) -> List[numpy.ndarray]:
#         """Build samples for a given feature."""
#         keys: List[Tuple[str, str]] = []
#         start: str = "-"

#         while len(keys) < self._limit:
#             batch = self._feature_store.get_keys(feature, start=start)

#             if not batch or batch[-1][0] == start:
#                 break

#             start = batch[-1][0]
#             keys += batch

#         keys = keys[self._offset : self._limit]  # NOTE: This could be dumped without data network serialization.

#         tensor: List[numpy.ndarray] = [self._feature_store.get(key[1]) for key in keys]
#         return numpy.array(tensor)  # type: ignore

#     def build(self) -> "Sampler":
#         """Compute all indexes and construct the object."""
#         self._data = numpy.array([self._sample_feature(feature) for feature in self._features])  # type: ignore
#         # NOTE: self.data.shape => (n_features, n_samples, dim_sample)

#         return self
