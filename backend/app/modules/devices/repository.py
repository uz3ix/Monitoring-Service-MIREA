from datetime import datetime
from sqlalchemy import func, or_, select, update
from sqlalchemy.orm import Session
from app.modules.devices.models import Device


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


def get_device_by_token_hash(db: Session, agent_token_hash: str) -> Device | None:
    statement = select(Device).where(Device.agent_token_hash == agent_token_hash)
    return db.scalar(statement)


def update_device_name(db: Session, device: Device, name: str) -> Device:
    device.name = name
    db.flush()
    return device


def get_device_for_update(db: Session, device_id: int) -> Device | None:
    statement = (
        select(Device).where(Device.id == device_id).with_for_update()
        .execution_options(populate_existing=True)
    )
    return db.scalar(statement)


def get_filtered_devices(db: Session, limit: int, offset: int, search: str, status: str | None, threshold: datetime):
    conditions = []
    if search:
        conditions.append(func.lower(Device.name).contains(search.lower(), autoescape=True))
    if status == "online":
        conditions.append(Device.last_seen_at >= threshold)
    elif status == "offline":
        conditions.append(or_(Device.last_seen_at.is_(None), Device.last_seen_at < threshold))
    total = db.scalar(select(func.count()).select_from(Device).where(*conditions))
    statement = select(Device).where(*conditions).order_by(Device.id).limit(limit).offset(offset)
    return list(db.scalars(statement).all()), total


def rotate_agent_token(db: Session, device: Device, token_hash: str) -> Device:
    device.agent_token_hash = token_hash
    db.flush()
    return device


def update_last_seen(db: Session, device_id: int, received_at: datetime) -> None:
    statement = update(Device).where(Device.id == device_id).values(
        last_seen_at=func.greatest(func.coalesce(Device.last_seen_at, received_at), received_at)
    )
    db.execute(statement)


def delete_device(db: Session, device: Device) -> None:
    db.delete(device)
    db.flush()
