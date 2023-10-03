import subprocess
from pathlib import Path
from threading import Thread

MOSQUITTO_PATH = "mosquitto"


class BrokerWrapper:
    def __init__(self, host, port=1883):
        self.port = port
        self.thread = None
        self.process = None

        self.on_start = None
        self.on_stop = None

    @property
    def is_running(self):
        return self.process is not None and self.process.poll() is None

    def _monitor(self, stream, header="[mosquitto]"):
        for line in iter(stream.readline, b''):
            print(header, line.decode('utf-8', errors='replace'), end='', flush=True)
        print(f"{header} Stream '{stream.name}' closed")
        if callable(self.on_stop): self.on_stop()

    def start(self):
        tmp_file = Path('tmp/mosquitto.conf')
        tmp_file.parent.mkdir(parents=True, exist_ok=True)
        with open(tmp_file, 'w') as f:
            f.write("listener 9002\n")
            f.write("protocol mqtt\n")
            f.write('\n')
            f.write(f"listener {self.port}\n")
            f.write("protocol websockets\n")
            f.write("allow_anonymous true\n")

        self.process = subprocess.Popen([MOSQUITTO_PATH, '-v', '-c', tmp_file],
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE)
        self.stdout_monitor = Thread(target=self._monitor, args=(self.process.stdout, "[mosquitto-stdout]"), daemon=True)
        self.stdout_monitor.start()
        self.stderr_monitor = Thread(target=self._monitor, args=(self.process.stderr, "[mosquitto-stderr]"), daemon=True)
        self.stderr_monitor.start()

        if callable(self.on_start): self.on_start()

    def stop(self):
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
        if self.stdout_monitor is not None:
            self.stdout_monitor.join()
            self.stdout_monitor = None
        if self.stderr_monitor is not None:
            self.stderr_monitor.join()
            self.stderr_monitor = None

        return self.process.poll()
