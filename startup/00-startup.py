import logging

from nslsii import configure_base
from IPython import get_ipython
from bluesky.callbacks.zmq import Publisher
import functools
from ophyd.signal import EpicsSignal, EpicsSignalRO
# Ben added so that Pymca would work
from suitcase.utils import MultiFileManager
from event_model import RunRouter
import event_model
from pathlib import Path

EpicsSignal.set_defaults(connection_timeout=10, timeout=60, write_timeout=60)
EpicsSignalRO.set_defaults(connection_timeout=10, timeout=60)

configure_base(
    get_ipython().user_ns,
    broker_name="opls",
    publish_documents_with_kafka=True,
    redis_url = "info.smi.nsls2.bnl.gov",
    redis_prefix = "opls-")

publisher = Publisher("xf12id1-ws2:5577")
RE.subscribe(publisher)

# ben commented this out on 3/24/2022 since it gave an error.  Not sure what it is for.
# Optionalte that when an item is *mutated* it is not immediately synced:
#        >>> d['sample'] = {"color": "red"}  # immediately synced
#        >>> d['sample']['shape'] = 'bar'  # not immediately synced
#        bumline_id"] = "OPLS"

# For debug mode
from bluesky.utils import ts_msg_hook
# RE.msg_hook = ts_msg_hook

# THIS NEEDS TO MOVE UPSTREAM
async def reset_user_position(msg):
    obj = msg.obj
    (val,) = msg.args

    old_value = obj.position
    obj.set_current_position(val)
    print(f"{obj.name} reset from {old_value:.4f} to {val:.4f}")

RE.register_command("reset_user_position", reset_user_position)

from pathlib import Path

import appdirs


try:
    from bluesky.utils import PersistentDict
except ImportError:
    import msgpack
    import msgpack_numpy
    import zict

    class PersistentDict(zict.Func):
        """
        A MutableMapping which syncs it contents to disk.
        The contents are stored as msgpack-serialized files, with one file per item
        in the mapping.
        Note that when an item is *mutated* it is not immediately synced:
        >>> d['sample'] = {"color": "red"}  # immediately synced
        >>> d['sample']['shape'] = 'bar'  # not immediately synced
        but that the full contents are synced to disk when the PersistentDict
        instance is garbage collected.
        """
        def __init__(self, directory):
            self._directory = directory
            self._file = zict.File(directory)
            self._cache = {}
            super().__init__(self._dump, self._load, self._file)
            self.reload()

            # Similar to flush() or _do_update(), but without reference to self
            # to avoid circular reference preventing collection.
            # NOTE: This still doesn't guarantee call on delete or gc.collect()!
            #       Explicitly call flush() if immediate write to disk required.
            def finalize(zfile, cache, dump):
                zfile.update((k, dump(v)) for k, v in cache.items())

            import weakref
            self._finalizer = weakref.finalize(
                self, finalize, self._file, self._cache, PersistentDict._dump)

        @property
        def directory(self):
            return self._directory

        def __setitem__(self, key, value):
            self._cache[key] = value
            super().__setitem__(key, value)

        def __getitem__(self, key):
            return self._cache[key]

        def __delitem__(self, key):
            del self._cache[key]
            super().__delitem__(key)

        def __repr__(self):
            return f"<{self.__class__.__name__} {dict(self)!r}>"

        @staticmethod
        def _dump(obj):
            "Encode as msgpack using numpy-aware encoder."
            # See https://github.com/msgpack/msgpack-python#string-and-binary-type
            # for more on use_bin_type.
            return msgpack.packb(
                obj,
                default=msgpack_numpy.encode,
                use_bin_type=True)

        @staticmethod
        def _load(file):
            return msgpack.unpackb(
                file,
                object_hook=msgpack_numpy.decode,
                raw=False)

        def flush(self):
            """Force a write of the current state to disk"""
            for k, v in self.items():
                super().__setitem__(k, v)

        def reload(self):
            """Force a reload from disk, overwriting current cache"""
            self._cache = dict(super().items())

#this replaces RE() <
from bluesky.utils import register_transform
register_transform('RE', prefix='<')

