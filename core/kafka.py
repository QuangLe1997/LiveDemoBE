# global variables
import asyncio
import datetime
import json
import logging
import time
from random import randint
from typing import Set, Any

import aiokafka
from aiokafka import AIOKafkaConsumer
from kafka import TopicPartition

from configs import settings
from dependencies import socket_manager

log = logging.getLogger(__name__)
# global variables
consumer_task = None
consumer = None
_state = 0
loop = asyncio.get_event_loop()
rtmp_ai_model_first_time = None
cache_messages = []
system_buff = 74
buffer_server = 60


async def kafka_consume():
    topic = settings.kafka.topic
    bootstrap_servers = settings.kafka.bootstrap_servers
    group = settings.kafka.group
    print(bootstrap_servers.split(",")[0])
    consumer = AIOKafkaConsumer(
        topic,
        loop=loop,
        bootstrap_servers=bootstrap_servers.split(",")[0],
        group_id=group,
    )
    # get cluster layout and join group KAFKA_CONSUMER_GROUP
    await consumer.start()
    try:
        # consume messages
        async for msg in consumer:
            print(msg)
            await socket_manager.emit("message", msg)
    except Exception as ex:
        print(ex)

    finally:
        # will leave consumer group; perform autocommit if enabled.
        await consumer.stop()


async def initialize():
    loop = asyncio.get_event_loop()
    global consumer
    group_id = f"{settings.kafka.group}-{randint(0, 10000)}"
    log.debug(
        f"Initializing KafkaConsumer for topic {settings.kafka.topic}, group_id {group_id}"
        f" and using bootstrap servers {settings.kafka.bootstrap_servers}"
    )
    consumer = aiokafka.AIOKafkaConsumer(
        settings.kafka.topic,
        loop=loop,
        bootstrap_servers=settings.kafka.bootstrap_servers,
        group_id=group_id,
    )
    # get cluster layout and join group
    await consumer.start()

    partitions: Set[TopicPartition] = consumer.assignment()
    nr_partitions = len(partitions)
    if nr_partitions != 1:
        log.warning(
            f"Found {nr_partitions} partitions for topic {settings.kafka.topic}. Expecting "
            f"only one, remaining partitions will be ignored!"
        )
    for tp in partitions:
        # get the log_end_offset
        end_offset_dict = await consumer.end_offsets([tp])
        end_offset = end_offset_dict[tp]
        if end_offset == 0:
            log.warning(
                f"Topic ({settings.kafka.topic}) has no messages (log_end_offset: "
                f"{end_offset}), skipping initialization ..."
            )
            return

        log.debug(f"Found log_end_offset: {end_offset} seeking to {end_offset-1}")
        consumer.seek(tp, end_offset - 1)
        msg = await consumer.getone()
        log.info(f"Initializing API with data from msg: {msg}")

        # update the API state
        await send_message_socket("init server success!")
        # socket_manager.emit("message", "init server success!")
        return


async def consume():
    global consumer_task
    await socket_manager.emit("message", "Star consumer")
    consumer_task = asyncio.create_task(send_consumer_message(consumer))


async def send_consumer_message(consumer):
    global rtmp_ai_model_first_time
    global cache_messages
    try:
        async for msg in consumer:
            if msg.key.decode("utf-8") == "time_info":
                rtmp_ai_model_first_time = msg.timestamp
                await send_message_socket(
                    {"time": rtmp_ai_model_first_time}, "time_info"
                )
            elif msg.key.decode("utf-8") == "meta_data":
                data = json.loads(msg.value)
                data["timestamp"] = msg.timestamp
                cache_messages.insert(0, data)
                if (
                        cache_messages[-1]["timestamp"] / 1000 + buffer_server
                        - (time.time() - system_buff)
                        < 0
                ):
                    cache_messages.pop()

                await send_message_socket(data, "message")
    except Exception as ex:
        log.error("Stopping consumer", str(ex))
    finally:
        # will leave consumer group; perform autocommit if enabled
        log.warning("Stopping consumer")
        await consumer.stop()


async def send_message_socket(message: Any, event: str = "message") -> None:
    await socket_manager.emit(event, message)


def get_ai_model_first_time():
    global rtmp_ai_model_first_time
    return rtmp_ai_model_first_time
