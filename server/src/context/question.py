import json
from pathlib import Path


class Question:
    last_id = 0

    def __init__(self, prompt, answers, img_path, img_is_local=True):
        Question.last_id += 1
        self.id = Question.last_id
        self.prompt = prompt
        self.answers = answers
        self.img_path = img_path
        self.img_is_local = img_is_local

    @property
    def as_dict(self):
        return {
            'id': self.id,
            'prompt': self.prompt,
            'answers': self.answers
        }

    @staticmethod
    def from_folder(question_folder: Path):
        info_path = question_folder / 'info.json'
        if not info_path.is_file():
            return None

        with open(info_path, 'r') as f:
            data = json.load(f)
        
        if 'image' in data:
            img_path = data['image']
        else:
            img_path = next((
                    f.absolute()
                    for f in question_folder.glob('img.*')
                    if f.suffix in ['.png', '.tif']
                ), None)
            if not img_path:
                return None

        return Question(
            prompt=data.get('question', None),
            answers=data.get('answers', None),
            img_path=img_path,
            img_is_local='image' not in data
        )
