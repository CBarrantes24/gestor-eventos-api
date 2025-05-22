from app.models.example import Example
from typing import List, Optional

class ExampleRepository:
    def __init__(self):
        self._db: List[Example] = []
        self._id_counter = 1

    def create(self, example: Example) -> Example:
        example.id = self._id_counter
        self._id_counter += 1
        self._db.append(example)
        return example

    def list(self) -> List[Example]:
        return self._db

    def get(self, example_id: int) -> Optional[Example]:
        return next((e for e in self._db if e.id == example_id), None)

    def update(self, example_id: int, data: Example) -> Optional[Example]:
        example = self.get(example_id)
        if example:
            example.name = data.name
            example.description = data.description
            return example
        return None

    def delete(self, example_id: int) -> bool:
        example = self.get(example_id)
        if example:
            self._db.remove(example)
            return True
        return False
