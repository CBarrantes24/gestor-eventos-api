from app.schemas.example import ExampleCreate
from app.models.example import Example as ExampleModel
from app.repositories.example_repository import ExampleRepository
from typing import List, Optional

class ExampleService:
    def __init__(self):
        self.repo = ExampleRepository()

    def create_example(self, data: ExampleCreate) -> ExampleModel:
        example = ExampleModel(name=data.name, description=data.description)
        return self.repo.create(example)

    def list_examples(self) -> List[ExampleModel]:
        return self.repo.list()

    def get_example(self, example_id: int) -> Optional[ExampleModel]:
        return self.repo.get(example_id)

    def update_example(self, example_id: int, data: ExampleCreate) -> Optional[ExampleModel]:
        example = ExampleModel(name=data.name, description=data.description)
        return self.repo.update(example_id, example)

    def delete_example(self, example_id: int) -> bool:
        return self.repo.delete(example_id)
