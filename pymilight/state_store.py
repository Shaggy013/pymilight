import json
import os

from pymilight.state import State

class StateStore:
    def __init__(self, persist_root):
        self._states = {}
        self._dirty = []
        self.persist_root = persist_root

        if not os.path.isdir(persist_root):
            os.makedirs(persist_root)

    def __getitem__(self, key):
        try:
            return self._states[key]
        except KeyError:
            self._states[key] = State()
            return self._states[key]

    def flush(self):
        for key in self._states:
            if not self._states[key].is_dirty:
                continue

            path = os.path.join(self.persist_root, "{0}-{1}-{2}.json".format(*key))
            with open(path, 'w') as fobj:
                vals = {}
                self._states[key].apply_fields(vals)
                self._states[key].clear_dirty()
                json.dump(vals, fobj)
