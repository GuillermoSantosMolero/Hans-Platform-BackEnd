from PyQt5.QtCore import QTimer, pyqtSlot
from PyQt5.QtWidgets import (QHBoxLayout, QLabel, QListWidget, QMainWindow,
                             QPushButton, QStatusBar, QVBoxLayout, QWidget)

from src.context import AppContext, Session
from src.services import start_services, stop_services

from .session import SessionListItem, SessionPanelWidget


class ServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_session = None

    def on_services_started(self, service):
        if 'broker' in service.__class__.__name__.lower():
            self.mqtt_status_lbl.setText('🟢 MQTT Broker')
            AppContext.mqtt_broker.on_stop = lambda: self.mqtt_status_lbl.setText('🔴 MQTT Broker')
        elif 'api' in service.__class__.__name__.lower():
            self.api_status_lbl.setText('🟢 HTTP API')
            AppContext.api_service.on_session_created = self.on_session_created
            self.session_list_add_btn.setEnabled(True)


    ### SESSION :: NEW

    def on_add_session_btn_clicked(self):
        session = Session()
        AppContext.sessions[session.id] = session
        self.on_session_created(session)
        self.session_list.setCurrentRow(self.session_list.count() - 1)

    @pyqtSlot(Session)
    def on_session_created(self, session):
        self.session_list.addItem(SessionListItem(session))


    ### SESSION :: SELECTED

    def on_session_list_item_changed(self, new_item: SessionListItem, old_item: SessionListItem):
        self.session_panel.set_session(new_item.session)
        self.session_panel.setHidden(False)


    ### UI EVENTS

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(100, lambda: start_services(self.on_services_started))

    def setupUI(self):
        self.setWindowTitle("HANS Platform - Coordinator")
        self.resize(800, 600)

        main_panel = QWidget(self)
        self.setCentralWidget(main_panel)
        main_panel_layout = QVBoxLayout(main_panel)

        session_main_panel = QWidget(main_panel)
        main_panel_layout.addWidget(session_main_panel)
        session_main_panel_layout = QHBoxLayout(session_main_panel)

        session_list_panel = QWidget(session_main_panel)
        session_main_panel_layout.addWidget(session_list_panel)
        session_list_panel_layout = QVBoxLayout(session_list_panel)

        self.session_list = QListWidget(session_list_panel)
        session_list_panel_layout.addWidget(self.session_list)
        self.session_list.currentItemChanged.connect(self.on_session_list_item_changed)

        self.session_list_add_btn = QPushButton(session_list_panel)
        session_list_panel_layout.addWidget(self.session_list_add_btn)
        self.session_list_add_btn.setText('New session')
        self.session_list_add_btn.setEnabled(False)
        self.session_list_add_btn.clicked.connect(self.on_add_session_btn_clicked)

        self.session_panel = SessionPanelWidget(parent=session_main_panel)
        session_main_panel_layout.addWidget(self.session_panel)
        self.session_panel.setHidden(True)

        services_status_panel = QWidget(main_panel)
        main_panel_layout.addWidget(services_status_panel)
        services_status_panel_layout = QVBoxLayout(services_status_panel)

        self.mqtt_status_lbl = QLabel(services_status_panel)
        services_status_panel_layout.addWidget(self.mqtt_status_lbl)
        self.mqtt_status_lbl.setText('🔴 MQTT Broker')

        self.api_status_lbl = QLabel(services_status_panel)
        services_status_panel_layout.addWidget(self.api_status_lbl)
        self.api_status_lbl.setText('🔴 HTTP API')

        self.statusbar = QStatusBar(self)
        self.setStatusBar(self.statusbar)

    def shutdown(self):
        stop_services()
