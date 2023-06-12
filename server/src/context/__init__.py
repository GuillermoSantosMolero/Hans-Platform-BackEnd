from argparse import Namespace
from pathlib import Path
from typing import Dict

from .participant import Participant
from .question import Question
from .session import Session

QUESTIONS_FOLDER = Path('questions')
SESSION_LOG_FOLDER = Path('session_log')

class AppContext:
    args = Namespace(
        mqtt_port=9001,
        api_port=8080,
    )

    mqtt_broker = None
    api_service = None

    sessions: 'Dict[Session]' = {}
    questions: 'Dict[Question]' = {}

    @staticmethod
    def reload_questions():
        AppContext.questions = {
        question.id: question for question in filter(
            lambda question: question is not None,
            map(
                lambda question_path: Question.from_folder(question_path),
                QUESTIONS_FOLDER.iterdir()
            )
        )
    }
