from enum import Enum


class Participant():
    last_id = 0

    class Status(Enum):
        JOINED = 'joined'
        READY = 'ready'
        ACTIVE = 'active'
        OFFLINE = 'offline'

    def __init__(self, username):
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

    @property
    def as_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'status': self._status.value,
        }
