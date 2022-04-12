import logging

from configs import settings
from core.kafka import initialize, consume, consumer_task, consumer
from dependencies import socket_manager

log = logging.getLogger(__name__)


async def handle_app_startup():
    """Start app"""
    log.info("Initializing API ...")
    log.info("setting", settings.server)
    await socket_manager.emit("message", "Star server")
    await initialize()
    await consume()
    log.info("End starting app ...")


async def handle_app_shutdown():
    """Shutdown app"""
    log.info("Shutting down API")
    if consumer_task:
        consumer_task.cancel()
    if consumer:
        await consumer.stop()
