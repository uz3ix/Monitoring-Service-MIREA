from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.modules.devices.models import Device
from app.modules.devices.schemas import DeviceCreate
from app.modules.devices.repository import create_device as create_device_record, get_device_by_id as get_device_record, get_devices as get_devices_record


def create_device(db: Session, data: DeviceCreate) -> Device:
    try:
        new_device = create_device_record(db, data.name)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return new_device


def get_device_by_id(db: Session, device_id: int) -> Device | None:
    return get_device_record(db, device_id)


def get_devices(db: Session, limit: int = 10, offset: int = 0) -> list[Device]:
    return get_devices_record(db, limit, offset)
