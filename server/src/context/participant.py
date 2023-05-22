from enum import Enum

from PyQt5.QtCore import QObject, pyqtSignal


class Participant(QObject):
    last_id = 0

    class Status(Enum):
        JOINED = 'joined'
        READY = 'ready'
        ACTIVE = 'active'
        OFFLINE = 'offline'

    on_status_changed = pyqtSignal(QObject, Status)

    def __init__(self, username):
        QObject.__init__(self)
        Participant.last_id += 1
        self.id = Participant.last_id
        self.username = username
        self._status = Participant.Status.JOINED

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        if status != self._status:
            self._status = status
            self.on_status_changed.emit(self, status)

    @property
    def as_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'status': self._status.value,
        }