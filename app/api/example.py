from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.example import ExampleCreate
from app.services.example_service import ExampleService
from app.models.example import Example

router = APIRouter(prefix="/examples", tags=["examples"])

service = ExampleService()

@router.post("/", response_model=Example)
def create_example(example: ExampleCreate):
    return service.create_example(example)

@router.get("/", response_model=List[Example])
def list_examples():
    return service.list_examples()

@router.get("/{example_id}", response_model=Example)
def get_example(example_id: int):
    result = service.get_example(example_id)
    if not result:
        raise HTTPException(status_code=404, detail="Example not found")
    return result

@router.put("/{example_id}", response_model=Example)
def update_example(example_id: int, example: ExampleCreate):
    return service.update_example(example_id, example)

@router.delete("/{example_id}")
def delete_example(example_id: int):
    service.delete_example(example_id)
    return {"ok": True}
