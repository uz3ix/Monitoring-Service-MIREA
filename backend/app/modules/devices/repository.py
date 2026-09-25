from sqlalchemy.orm import Session
from app.modules.devices.models import Device
from sqlalchemy import select


def create_device(db: Session, name: str, agent_token_hash: str) -> Device:
    new_device = Device(name=name, agent_token_hash=agent_token_hash)
    db.add(new_device)
    db.flush()

    return new_device


def get_device_by_id(db: Session, device_id: int) -> Device | None:
    return db.get(Device, device_id)


def get_devices(db: Session, limit: int = 10, offset: int = 0) -> list[Device]:
    statement = select(Device).order_by(Device.id).limit(limit).offset(offset)
    result = db.scalars(statement)
    return list(result.all())


def get_device_by_token_hash(db: Session,
                             agent_token_hash: str) -> Device | None:
    statement = select(Device).where(
        Device.agent_token_hash == agent_token_hash
    )
    return db.scalar(statement)
