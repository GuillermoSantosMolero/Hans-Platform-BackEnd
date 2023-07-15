from argparse import Namespace
from pathlib import Path
from typing import Dict

from .participant import Participant
from .question import Question
from .session import Session
from .Collection import Collection
COLLECTION_FOLDER = Path('questions')
SESSION_LOG_FOLDER = Path('session_log')

class AppContext:
    args = Namespace(
        mqtt_port=9001,
        api_port=8080,
    )

    mqtt_broker = None
    api_service = None

    sessions: 'Dict[Session]' = {}
    collections: 'Dict[Collection]' = {}

    @staticmethod
    def reload_collections():
        AppContext.collections = {
        collection.id: collection for collection in filter(
            lambda collection: collection is not None,
            map(
                lambda collection_path: Collection.from_folder(collection_path),
                COLLECTION_FOLDER.iterdir()
            )
        )
    }
