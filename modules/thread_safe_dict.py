import threading
import time

class ThreadSafeDict:
    def __init__(self, expiry_seconds=5, cleanup_interval=5):
        self.lock = threading.RLock()
        self.store = {}  # key -> (value, timestamp)
        self.expiry_seconds = expiry_seconds
        self.cleanup_interval = cleanup_interval
        self._stop_event = threading.Event()
        self._cleanup_thread = threading.Thread(target=self._cleanup, daemon=True)
        self._cleanup_thread.start()

    def set(self, key, value):
        with self.lock:
            self.store[key] = (value, time.time())

    def get(self, key):
        with self.lock:
            entry = self.store.get(key)
            return entry[0] if entry else None

    def remove(self, key):
        with self.lock:
            return self.store.pop(key, None)

    def items(self):
        with self.lock:
            return [(k, v[0]) for k, v in self.store.items()]

    def __contains__(self, key):
        with self.lock:
            return key in self.store

    def __repr__(self):
        with self.lock:
            return repr({k: v[0] for k, v in self.store.items()})

    def _cleanup(self):
        while not self._stop_event.is_set():
            now = time.time()
            with self.lock:
                keys_to_delete = [k for k, (_, ts) in self.store.items() if now - ts > self.expiry_seconds]
                for k in keys_to_delete:
                    del self.store[k]
            time.sleep(self.cleanup_interval)

    def stop_cleanup(self):
        self._stop_event.set()
        self._cleanup_thread.join()
