import multiprocessing

bind = "0.0.0.0:8000"
workers = 5
accesslog = "-"
proc_name = "ArtmapOnline"

_manager = multiprocessing.Manager()
shared_cache = _manager.dict()


def on_starting(server):
    import builtins
    builtins.GLOBAL_SHARED_CACHE = shared_cache
