from typing import Callable, Union

import src.context as ctx
from .api import ServerAPI
from .mqtt import BrokerWrapper


def start_services(
    on_start_cb: Callable[[Union[BrokerWrapper, ServerAPI]], None]=None
):
    print("Starting services")
    ctx.AppContext.mqtt_broker = BrokerWrapper('localhost', ctx.AppContext.args.mqtt_port)
    if on_start_cb:
        ctx.AppContext.mqtt_broker.on_start = lambda: on_start_cb(ctx.AppContext.mqtt_broker)
    ctx.AppContext.mqtt_broker.start()

    ctx.AppContext.api_service = ServerAPI(port=ctx.AppContext.args.api_port)
    if on_start_cb:
        ctx.AppContext.api_service.on_start.connect(lambda: on_start_cb(ctx.AppContext.api_service))
    ctx.AppContext.api_service.start()

    print("Services up and running")

def stop_services():
    if ctx.AppContext.mqtt_broker:
        ctx.AppContext.mqtt_broker.stop()

    if ctx.AppContext.api_service:
        ctx.AppContext.api_service.shutdown()