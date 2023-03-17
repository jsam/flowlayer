import os
import time
import uuid
from typing import List, Tuple

import numpy
import redisai as rai

from ilflow.core.api import FeatureStoreAPI, NetworkAPI


class FeatureStore(FeatureStoreAPI):
    """Feature store."""

    def __init__(self) -> None:
        """Feature store constructor."""
        server: str = os.getenv("REDISAI_URI", "0.0.0.0:6379")
        host, port = server.split(":")
        self._conn = rai.Client(host=host, port=int(port))  # type: ignore

        super().__init__()

    def set(self, tensor: numpy.ndarray, network: NetworkAPI) -> Tuple[str, str]:
        """Store tensor to the feature store."""
        timestamp: str = str(int(time.time() * 1e3))  # NOTE: Milliseconds
        key: str = f"{network.identifier}-{timestamp}-{uuid.uuid4().hex}"

        self._conn.tensorset(key, tensor)  # type: ignore
        stream_id: bytes = self._conn.xadd(network.identifier, {"key": key})  # type: ignore

        return stream_id.decode("utf-8"), key

    def get(self, key: str) -> numpy.ndarray:
        """Get tensor from the store."""
        return self._conn.tensorget(key, as_numpy=True)  # type: ignore

    def get_keys(self, network: NetworkAPI, start: str = "-", end: str = "+", limit: int = 500) -> List[Tuple[str, str]]:
        """Get slice of keys for a given features."""
        results: List[Tuple[str, str]] = [
            (t[0].decode("utf-8"), t[1][b"key"].decode("utf-8"))  # type: ignore
            for t in self._conn.xrange(network.identifier, min=start, max=end, count=limit)  # type: ignore
        ]

        return results
