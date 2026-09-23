from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.modules.devices.models import Device
from app.modules.devices.schemas import DeviceCreate
from app.modules.devices.repository import create_device as create_device_record


def create_device(db: Session, data: DeviceCreate) -> Device:
    try:
        new_device = create_device_record(db, data.name)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return new_device
