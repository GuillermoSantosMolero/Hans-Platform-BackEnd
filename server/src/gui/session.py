from PyQt5.QtCore import QTime, QTimer, pyqtSlot
from PyQt5.QtWidgets import (QComboBox, QGridLayout, QGroupBox, QLabel,
                             QLineEdit, QListWidget, QListWidgetItem,
                             QPushButton, QStackedWidget, QVBoxLayout, QWidget)
from PyQt5 import QtGui

from src.context import AppContext, Participant, Session
from src.context.session import SessionCommunicator

from .participant import ParticipantWidget


class SessionListItem(QListWidgetItem):
    def __init__(self, session: Session):
        super().__init__()
        self.session = session
        self.setText(f"Session {session.id}")

class SessionPanelWidget(QWidget):
    def __init__(self,
        session: Session = None,
        parent: QWidget = None
    ):
        super().__init__(parent)
        self.session = None
        self.duration_timer = QTimer(self)
        self.duration_timer.timeout.connect(self.on_duration_timer_timeout)

        self.setupUI()

        if session is not None:
            self.set_session(session)

    def set_connection_status(self, status: SessionCommunicator.Status):
        self.connection_txt.setText({
            SessionCommunicator.Status.DISCONNECTED: '🔴 Disconnected',
            SessionCommunicator.Status.CONNECTED: '🔵 Connected',
            SessionCommunicator.Status.SUBSCRIBED: '🟢 Subscribed',
        }[status])

    @pyqtSlot(Session, SessionCommunicator.Status)
    def on_connection_status_changed(self, session: Session, status: SessionCommunicator.Status):
        self.set_connection_status(status)

    def set_status(self, status: Session.Status):
        self.status_txt.setText({
            Session.Status.WAITING: 'Waiting for participants to join',
            Session.Status.ACTIVE: 'Active'
        }[status])

    @pyqtSlot(Session, Session.Status)
    def on_status_changed(self, session: Session, status: Session.Status):
        self.set_status(status)
        self.duration_txt.setEnabled(status == Session.Status.WAITING)
        self.question_cbbox.setEnabled(session.status == Session.Status.WAITING)

    @pyqtSlot()
    def on_duration_timer_timeout(self):
        if not self.session: return

        remaining_ms = max(0, (self.session.duration * 1000) - self.session.timer.elapsed())
        self.duration_timer_lbl.setText(QTime.fromMSecsSinceStartOfDay(remaining_ms).toString("mm:ss"))

        if remaining_ms == 0:
            self.start_btn.setEnabled(False)
            self.session.stop()

    ### SET QUESTION

    def on_question_changed(self, question_id: str):
        self.question_cbbox.setEnabled(False)
        if question_id == '<none>':
            self.session.active_question = None
        else:
            try:
                self.session.active_question = int(question_id)
            except (ValueError, KeyError):
                self.session.active_question = None
                self.question_cbbox.setCurrentIndex(0)

    @pyqtSlot(Session, bool)
    def on_question_notified(self, session, notified):
        self.question_cbbox.setEnabled(True)

    ### ADD PARTICIPANT

    def add_participant_widget(self, participant: Participant):
        widget = ParticipantWidget(participant)
        item = QListWidgetItem(self.participants_list)
        item.setSizeHint(widget.sizeHint())
        self.participants_list.addItem(item)
        self.participants_list.setItemWidget(item, widget)

    @pyqtSlot(Session, Participant)
    def on_participant_joined(self, session, participant):
        if session != self.session:
            return

        self.add_participant_widget(participant)
        self.participants_ready_txt.setText(f"{session.ready_participants_count}/{len(session.participants)} participants")

    @pyqtSlot(int, int, int)
    def on_participants_ready_changed(self, ready_count, offline_count, total_count):
        if self.session.status == Session.Status.WAITING:
            self.start_btn.setEnabled(((ready_count + offline_count) == total_count) and ready_count > 0)
            self.participants_ready_txt.setText(f"{ready_count}/{total_count} participants")

    ### START / STOP

    def on_start_btn_clicked(self):
        self.start_btn.setEnabled(False)
        if self.session.status == Session.Status.WAITING:
            self.session.duration = int(self.duration_txt.text())
            self.session.start()
        elif self.session.status == Session.Status.ACTIVE:
            self.session.stop()

    @pyqtSlot(Session, bool)
    def on_start(self, session, started):
        self.start_btn.setText('Stop')
        self.start_btn.setEnabled(True)
        self.duration_stack.setCurrentIndex(1)
        self.duration_timer.start(10)

    @pyqtSlot(Session, bool)
    def on_stop(self, session, stopped):
        self.start_btn.setText('Start')
        self.start_btn.setEnabled(True)
        self.duration_stack.setCurrentIndex(0)
        self.duration_timer.stop()


    ### UI SETUP

    def set_session(self, session: Session):
        if self.session is not None:
            self.session.on_connection_status_changed.disconnect()
            self.session.on_status_changed.disconnect()
            self.session.on_question_notified.disconnect()
            self.session.on_participant_joined.disconnect()
            self.session.on_participants_ready_changed.disconnect()
            self.session.on_start.disconnect()
            self.session.on_stop.disconnect()

        self.session = session
        if session is None:
            return

        self.id_txt.setText(str(session.id))
        self.set_connection_status(session.communicator.status)
        self.duration_txt.setText(str(session.duration))
        self.duration_txt.setEnabled(session.status == Session.Status.WAITING)
        self.set_status(session.status)
        self.question_cbbox.setCurrentText(str(session.active_question.id) if session.active_question else '<none>')
        self.question_cbbox.setEnabled(session.status == Session.Status.WAITING)

        # Refresh participants list
        self.participants_list.clear()
        for participant in session.participants.values():
            self.add_participant_widget(participant)

        # Update participants ready count
        participants_ready_count = session.ready_participants_count
        participants_offline_count = session.offline_participants_count
        participants_total_count = len(session.participants)
        self.participants_ready_txt.setText(f"{participants_ready_count}/{participants_total_count} participants")

        # Configure Start/Stop button
        if session.status == Session.Status.WAITING:
            self.start_btn.setText('Start')
            self.start_btn.setEnabled(((participants_ready_count + participants_offline_count) == participants_total_count) and (participants_total_count > 0))
        elif session.status == Session.Status.ACTIVE:
            self.start_btn.setText('Stop')
            self.start_btn.setEnabled(True)

        session.on_connection_status_changed.connect(self.on_connection_status_changed)
        session.on_status_changed.connect(self.on_status_changed)
        session.on_question_notified.connect(self.on_question_notified)
        session.on_participant_joined.connect(self.on_participant_joined)
        session.on_participants_ready_changed.connect(self.on_participants_ready_changed)
        session.on_start.connect(self.on_start)
        session.on_stop.connect(self.on_stop)

    def setupUI(self):
        main_panel_layout = QVBoxLayout(self)

        details_panel = QGroupBox(self)
        main_panel_layout.addWidget(details_panel)
        details_panel_layout = QGridLayout(details_panel)
        details_panel.setTitle('Session details')

        details_row = 0
        id_lbl = QLabel(details_panel)
        details_panel_layout.addWidget(id_lbl, details_row, 0)
        id_lbl.setText('ID:')

        self.id_txt = QLineEdit(details_panel)
        details_panel_layout.addWidget(self.id_txt, details_row, 1)

        ## Connection status
        details_row += 1
        connection_lbl = QLabel(details_panel)
        details_panel_layout.addWidget(connection_lbl, details_row, 0)
        connection_lbl.setText('Connection:')

        self.connection_txt = QLabel(details_panel)
        details_panel_layout.addWidget(self.connection_txt, details_row, 1)

        ## Duration
        details_row += 1
        duration_lbl = QLabel(details_panel)
        details_panel_layout.addWidget(duration_lbl, details_row, 0)
        duration_lbl.setText('Duration:')

        self.duration_stack = QStackedWidget(details_panel)
        details_panel_layout.addWidget(self.duration_stack, details_row, 1)

        self.duration_txt = QLineEdit(self.duration_stack)
        self.duration_txt.setValidator(QtGui.QDoubleValidator())
        self.duration_stack.addWidget(self.duration_txt)
        self.duration_stack.setCurrentIndex(0)

        self.duration_timer_lbl = QLabel(self.duration_stack)
        self.duration_stack.addWidget(self.duration_timer_lbl)

        ## Session status
        details_row += 1
        status_lbl = QLabel(details_panel)
        details_panel_layout.addWidget(status_lbl, details_row, 0)
        status_lbl.setText('Status:')

        self.status_txt = QLabel(details_panel)
        details_panel_layout.addWidget(self.status_txt, details_row, 1)

        ## Question
        details_row += 1
        question_lbl = QLabel(details_panel)
        details_panel_layout.addWidget(question_lbl, details_row, 0)
        question_lbl.setText("Question:")

        self.question_cbbox = QComboBox(details_panel)
        details_panel_layout.addWidget(self.question_cbbox, details_row, 1)
        self.question_cbbox.addItem('<none>')
        self.question_cbbox.addItems([str(id) for id in AppContext.questions])
        self.question_cbbox.currentTextChanged.connect(self.on_question_changed)

        ## Participants ready count
        details_row += 1
        participants_ready_lbl = QLabel(details_panel)
        details_panel_layout.addWidget(participants_ready_lbl, details_row, 0)
        participants_ready_lbl.setText("Ready:")

        self.participants_ready_txt = QLabel(details_panel)
        details_panel_layout.addWidget(self.participants_ready_txt, details_row, 1)

        ## Start button
        self.start_btn = QPushButton(self)
        main_panel_layout.addWidget(self.start_btn)
        self.start_btn.setText('Start')
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.on_start_btn_clicked)

        ## Participants list
        self.participants_list = QListWidget(self)
        main_panel_layout.addWidget(self.participants_list)
