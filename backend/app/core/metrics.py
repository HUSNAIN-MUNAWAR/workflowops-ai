from collections import Counter
from threading import Lock

class Metrics:
    def __init__(self):
        self._counter = Counter()
        self._lock = Lock()
    def inc(self, name: str, value: int = 1):
        with self._lock: self._counter[name] += value
    def set(self, name: str, value: int):
        with self._lock: self._counter[name] = value
    def as_prometheus(self) -> str:
        with self._lock:
            lines = []
            for key, value in sorted(self._counter.items()):
                lines += [f"# TYPE {key} counter", f"{key} {value}"]
            return "\n".join(lines) + "\n"
metrics = Metrics()
