from abc import ABC, abstractmethod
from threading import Thread
from typing import Callable, Dict

import paho.mqtt.client as mqtt
from paho.mqtt.client import CONNACK_ACCEPTED, MQTT_ERR_SUCCESS


class MQTTClient(ABC):
    @abstractmethod
    def connection_handler(self, connected: bool, reason: int) -> None: ...

    def __init__(self, host='localhost', port=1883):
        self.host = host
        self.port = port
        self.connected = False
        self.pending_subscriptions: Dict[int, Callable[[bool], None]] = {}
        self.client = mqtt.Client(transport="websockets")
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe
        self.client.ws_set_options(path="/")

    def start(self):
        self.client.connect_async(self.host, self.port, 60)
        self.client.loop_start()

    def shutdown(self):
        self.client.loop_stop()

    def on_connect(self, client, obj, flags, rc):
        self.connected = rc == CONNACK_ACCEPTED
        self.connection_handler(self.connected, rc)

    def on_disconnect(self, client, obj, rc):
        self.connected = False
        self.connection_handler(False, rc)

    def on_subscribe(self, client, obj, message_id, granted_qos):
        if message_id not in self.pending_subscriptions:
            return
        self.pending_subscriptions[message_id](True)

    def subscribe(self, topic, callback: Callable[[bool], None] = None):
        result, message_id = self.client.subscribe(topic)
        if callback:
            if result == MQTT_ERR_SUCCESS:
                self.pending_subscriptions[message_id] = callback
            else:
                callback(False)

    def publish_sync(self, topic, msg, callback: Callable[[bool], None] = None):
        msg_handle = self.client.publish(topic, msg)
        msg_handle.wait_for_publish()
        if callback: callback(True) # TODO: Send false if message could not be queued

    def publish(self, topic, msg, post_callback=None):
        Thread(
            target=self.publish_sync,
            args=(topic, msg, post_callback),
            daemon=True
        ).start()
