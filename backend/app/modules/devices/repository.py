from sqlalchemy.orm import Session
from app.modules.devices.models import Device


def create_device(db: Session, name: str) -> Device:
    new_device = Device(name=name)
    db.add(new_device)
    db.flush()
    
    return new_device