from app.services.user_service import UserService
from app.schemas.user import UserCreate

def test_create_event():
    service = UserService()

    
    data = UserCreate(
        identificacion="111111111",
        nombre="Carlos Test",
        email="carlos@test.com",
        rol="Administrador",
        password="Abc123*",
    )
    
    
    event = service.create_user(data)
    print(event)
    assert event.id is not None
    assert event.identificacion == "111111111"
    assert event.email == "carlos@test.com"
    assert event.rol == "Administrador"
    
