import sys
from argparse import ArgumentParser
from .services import start_services,stop_services
from .context import AppContext

if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--api-port', dest='api_port', type=int,
                        help=f"HTTP API port. Default: {AppContext.args.api_port}",
                        default=AppContext.args.api_port)
    parser.add_argument('--mqtt-port', dest='mqtt_port', type=int,
                        help=f"MQTT Broker port. Default: {AppContext.args.mqtt_port}",
                        default=AppContext.args.mqtt_port)
    AppContext.args = parser.parse_args()
    AppContext.reload_questions()
   
    try:
        start_services();
    except KeyboardInterrupt:
        stop_services();
