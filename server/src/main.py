import sys
from argparse import ArgumentParser

from PyQt5.QtWidgets import QApplication

from .context import AppContext
from .gui import ServerGUI

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

    app = QApplication(sys.argv)

    gui = ServerGUI()
    gui.setupUI()
    gui.show()

    try:
        app.exec()
    except KeyboardInterrupt:
        pass
    finally:
        gui.shutdown()
