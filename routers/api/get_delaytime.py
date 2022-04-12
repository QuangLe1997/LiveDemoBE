import datetime
from time import process_time

from fastapi import APIRouter, Body, Depends
from starlette.background import BackgroundTasks

from core.kafka import get_ai_model_first_time, cache_messages
from core.socket import SocketManager
from dependencies import (
    get_socket,
    get_delay_buff,
    set_delay_buff,
    get_group_pixel,
    set_group_pixel,
)
from models.base_response import BaseResponseData
from utils import create_aliased_response

router = APIRouter()
hls_start_time = 0
rtmp_start_time = 0
hls_url = None
products = []


def delay_stream(hls: str, rtmp: str):
    import cv2

    global hls_start_time
    global rtmp_start_time
    global hls_url
    hls_url = hls

    hls_ready = False
    hls_time = 0
    rtmp_time = 0
    rtmp_ready = False
    start = process_time()
    while not hls or not rtmp_ready:
        try:
            if not rtmp_ready:
                try:
                    cap = cv2.VideoCapture(rtmp)
                    if cap.isOpened():
                        rtmp_ready = True
                        rtmp_time = datetime.datetime.utcnow()
                except Exception:
                    pass
            if not hls_ready:
                try:
                    cap2 = cv2.VideoCapture(hls)
                    if cap2.isOpened():
                        hls_ready = True
                        hls_time = datetime.datetime.utcnow()
                except Exception:
                    pass
        except Exception:
            pass
        if process_time() - start > 60:
            break

    if hls_ready and rtmp_ready:
        hls_start_time = hls_time.timestamp()
        rtmp_start_time = rtmp_time.timestamp()
    else:
        hls_start_time = 0
        rtmp_start_time = 0
    return


@router.get(
    "/healthcheck",
    response_model=BaseResponseData,
    tags=["Wrapper API"],
)
async def health_check():
    """Add multiple task to task-pipeline"""
    return create_aliased_response(
        BaseResponseData(
            code=0,
            message="success",
            result={"health_check": "Oke"},
        )
    )


@router.post(
    "/live/start-livestream",
    response_model=BaseResponseData,
    tags=["Wrapper API"],
)
async def start_livestream(
    *,
    body: dict = Body(...),
    background_tasks: BackgroundTasks,
):
    """Add multiple task to task-pipeline"""
    global rtmp_start_time
    global hls_start_time
    rtmp_start_time = None
    hls_start_time = None
    background_tasks.add_task(delay_stream, body.get("hls"), body.get("rtmp"))
    # background_tasks.add_task(delay_stream_hls, body.get("hls"))
    return create_aliased_response(
        BaseResponseData(
            code=0,
            message="success",
            result={},
        )
    )


@router.get(
    "/live/config-data",
    response_model=BaseResponseData,
    tags=["Wrapper API"],
)
async def get_livestream_config():
    """Add multiple task to task-pipeline"""
    global hls_start_time
    global rtmp_start_time
    if hls_start_time and rtmp_start_time:
        delay = hls_start_time - rtmp_start_time
    else:
        delay = -1
    result = {
        "hls_url": hls_url,
        "hls_start": hls_start_time,
        "worker_start": get_ai_model_first_time(),
        "rtmp_start": rtmp_start_time,
        "delay": delay,
        "group_pixel": get_group_pixel(),
        "delay_buff": get_delay_buff(),
    }
    return create_aliased_response(
        BaseResponseData(
            code=0,
            message="success",
            result=result,
        )
    )


@router.post(
    "/live/config",
    response_model=BaseResponseData,
    tags=["Wrapper API"],
)
async def update_livestream_config(
    *, body: dict = Body(...), socket_mng: SocketManager = Depends(get_socket)
):
    """Add multiple task to task-pipeline"""

    global hls_start_time
    global rtmp_start_time
    if body.get("delay_buff", None) is not None:
        set_delay_buff(int(body.get("delay_buff")))
    # if body.get("delay", None) is not None:
    #     hls_start_time = body.get("delay")
    #     rtmp_start_time = 0
    if body.get("group_pixel", None) is not None:
        set_group_pixel(float(body.get("group_pixel")))

    await socket_mng.emit(
        "config",
        {
            "hls_url": hls_url,
            "hls_start": hls_start_time,
            "worker_start": get_ai_model_first_time(),
            "rtmp_start": rtmp_start_time,
            "delay": hls_start_time - rtmp_start_time,
            "group_pixel": get_group_pixel(),
            "delay_buff": get_delay_buff(),
        },
    )

    return create_aliased_response(
        BaseResponseData(
            code=0,
            message="success",
            result={
                "hls_url": hls_url,
                "hls_start": hls_start_time,
                "worker_start": get_ai_model_first_time(),
                "rtmp_start": rtmp_start_time,
                "delay": hls_start_time - rtmp_start_time,
                "group_pixel": get_group_pixel(),
                "delay_buff": get_delay_buff(),
            },
        )
    )


@router.get(
    "/live/messages",
    response_model=BaseResponseData,
    tags=["Wrapper API"],
)
async def get_messages():
    """Add multiple task to task-pipeline"""

    return create_aliased_response(
        BaseResponseData(
            code=0,
            message="success",
            result={"messages": cache_messages, "count": len(cache_messages)},
        )
    )


@router.get(
    "/live/products",
    response_model=BaseResponseData,
    tags=["Wrapper API"],
)
async def get_products():
    """get product mapping"""

    return create_aliased_response(
        BaseResponseData(
            code=0,
            message="success",
            result=products,
        )
    )


@router.put(
    "/live/products",
    response_model=BaseResponseData,
    tags=["Wrapper API"],
)
async def update_products(
    *, body: dict = Body(...), socket_mng: SocketManager = Depends(get_socket)
):
    """update product mapping"""
    global products
    if bool(body.get("products")):
        products = body.get("products", [])
        socket_mng.emit("products", products)
    return create_aliased_response(
        BaseResponseData(
            code=0,
            message="success",
            result=products,
        )
    )
