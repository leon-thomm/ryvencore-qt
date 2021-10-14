"""
These classes are used to abstract away threaded communication between GUI and  and backend components.
The backend can run trigger method executions in the frontend through the backend interface, and the
frontend can do the same respectively through the frontend interface.
Notice that both classes abstract away the concurrency of the threads such that they wait for some
container object to be set (the payload) with the return of the triggered method. This enables
calling methods of objects from another thread as if they lived in the same thread.
"""

from qtpy.QtCore import QObject, Signal

from .utils import Container, wait_until


class SessionThreadInterface_Backend(QObject):
    """lives in the session's thread"""

    run_signal = Signal(object, object, object)
    callback_signal = Signal(object)

    def __init__(self):
        super().__init__()

        self.frontend = SessionThreadInterface_Frontend(self)
        self.run_signal.connect(self.frontend.run_in_frontend)

    # run in frontend
    def run(self, target_method, args: tuple = (), wait=True):
        """run some method in frontend thread"""
        resp_container = Container()
        self.run_signal.emit(target_method, tuple(args), resp_container)

        if wait:
            wait_until(resp_container.is_set)
            return resp_container.payload

        return None

    # run in backend
    def run_in_backend(self, target_method, args: tuple, resp_container: Container, callback=None):

        ret = target_method(*args)

        if resp_container:
            resp_container.set(ret)

        if callback is not None:
            self.callback_signal.connect(callback)
            self.callback_signal.emit(ret)
            self.callback_signal.disconnect(callback)


class SessionThreadInterface_Frontend(QObject):
    """lives in the GUI thread and triggers method executions in the session thread"""

    run_signal = Signal(object, object, object, object)

    def __init__(self, backend_component: SessionThreadInterface_Backend):
        super().__init__()

        self.backend = backend_component
        self.run_signal.connect(self.backend.run_in_backend)

    # run in backend
    def run(self, target_method, args: tuple = (), wait=True, callback=None):
        """
        Runs some method in backend thread
        `wait` causes the frontend thread to wait until the execution finished.
        `callback` is optional and can be a function that gets called after the execution was completed.
        """

        resp_container = Container()
        self.run_signal.emit(target_method, tuple(args), resp_container, callback)

        if wait:
            wait_until(resp_container.is_set)
            return resp_container.payload

        return None

    # run in frontend
    def run_in_frontend(self, target_method, args: tuple = (), resp_container: Container = None):

        ret = target_method(*args)

        if resp_container:
            resp_container.set(ret)

    # CONVENIENCE METHODS
    def trigger_node_action(self, method, data=None):
        self.run(method, args=(data,) if data is not None else ())
