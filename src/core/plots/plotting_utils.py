import pickle

_PLOT_QUEUE = None
_LOCK_QUEUE = None


def set_plot_dispatch(plot_queue=None, lock_queue=None):
    global _PLOT_QUEUE, _LOCK_QUEUE
    _PLOT_QUEUE = plot_queue
    _LOCK_QUEUE = lock_queue


def plt_show(fig):
    import matplotlib.pyplot as plt
    import multiprocessing as mp

    if fig is None:
        fig = plt.gcf()

    if mp.current_process().name == "MainProcess":
        plt.show()
    else:
        raw = pickle.dumps(fig)
        _PLOT_QUEUE.put(("figure", raw))
        plt.close(fig)
        _LOCK_QUEUE.get()
