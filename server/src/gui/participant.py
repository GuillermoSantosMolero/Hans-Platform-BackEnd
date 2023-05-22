from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QWidget

from src.context import Participant


class ParticipantWidget(QWidget):
    def __init__(self,
        participant,
        parent=None
    ):
        super().__init__(parent)
        self.participant = participant
        self.participant.on_status_changed.connect(self.on_status_changed)

        main_layout = QHBoxLayout(self)

        id_label = QLabel(self)
        main_layout.addWidget(id_label)
        id_label.setText(str(participant.id))

        username_label = QLabel(self)
        main_layout.addWidget(username_label)
        username_label.setText(participant.username)

        self.status_label = QLabel(self)
        main_layout.addWidget(self.status_label)
        self.status_label.setText(participant.status.value)

    @pyqtSlot(Participant, Participant.Status)
    def on_status_changed(self, participant, status):
        self.status_label.setText(status.value)
