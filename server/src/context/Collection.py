import os
from typing import Dict
from pathlib import Path

from .question import Question


class Collection:

    def __init__(self, id, questions):
        self.id = id
        self.questions: Dict[str, Question] = questions
        self.firstQuestionId = next(iter(self.questions.values())).id

    @property
    def as_dict(self):
        return {
            'id': self.id,
            'questions': [question.__json__() for question in self.questions.values()],
            'firstQuestionId': self.firstQuestionId
        }
    
    @staticmethod
    def from_folder(collection_folder: Path):
        logs = [name for name in os.listdir(collection_folder) if os.path.isdir(os.path.join(collection_folder, name))]
        questions: Dict[str, Question] = {}
        for log in logs:
            log_folder = collection_folder / log
            question = Question.from_folder(log_folder)
            questions[question.id] = question
        collection_name = collection_folder.parts[-1]
        return Collection(
            id=collection_name,
            questions=questions
        )