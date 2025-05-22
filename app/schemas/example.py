from sqlmodel import SQLModel

class ExampleBase(SQLModel):
    name: str
    description: str | None = None

class ExampleCreate(ExampleBase):
    pass

