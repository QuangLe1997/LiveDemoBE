from core.socket import SocketManager, handle_connect

SOCKET_INST = None
DELAY_HLS_RTMP = 7.5
DELAY_BUFF = 50
GROUP_PIXEL = 0.3


def get_socket():
    global SOCKET_INST
    if not SOCKET_INST:
        SOCKET_INST = SocketManager()
        SOCKET_INST.on("connect", handler=handle_connect)
        return SOCKET_INST
    return SOCKET_INST


socket_manager = get_socket()


def get_delay_buff():
    return DELAY_BUFF


def set_delay_buff(data):
    global DELAY_BUFF
    DELAY_BUFF = data


def get_group_pixel():
    return GROUP_PIXEL


def set_group_pixel(data):
    global GROUP_PIXEL
    GROUP_PIXEL = data
