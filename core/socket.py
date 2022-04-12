import logging

import socketio

logger = logging.getLogger("main")


def handle_connect(sid, environ, *args):
    # print("connect", args)
    # print(environ)
    # socket_manager.send(
    #     data={
    #         "hls_start": hls_start_time,
    #         "rtmp_start": rtmp_start_time,
    #         "delay": delay_time,
    #     },
    #     to=sid,
    # )
    logger.info(f"Socket connected with sid {sid}")


def handle_new_msg(sid, environ):
    # print(environ)
    logger.info(f"handle_new_msg {sid}")


class SocketManager:
    def __init__(self):
        self.server = socketio.AsyncServer(
            cors_allowed_origins="*",
            async_mode="asgi",
            logger=True,
            engineio_logger=True,
        )
        self.app = socketio.ASGIApp(self.server)

    @property
    def on(self):
        return self.server.on

    @property
    def emit(self):
        return self.server.emit

    @property
    def send(self):
        return self.server.send

    def mount_to(self, path: str, app: socketio.ASGIApp):
        app.mount(path, self.app)
