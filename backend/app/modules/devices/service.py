from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from psycopg.errors import UniqueViolation
from app.modules.devices.models import Device
from app.modules.devices.schemas import DeviceCreate
from app.modules.devices.exceptions import AgentTokenAlreadyExistsError
from app.core.security import hash_agent_token
from app.modules.devices.repository import (
    create_device as create_device_record,
    get_device_by_id as get_device_record,
    get_devices as get_devices_record,
    get_device_by_token_hash as get_device_by_token_hash_record
)


def create_device(db: Session, data: DeviceCreate) -> Device:
    try:
        new_device = create_device_record(
            db, data.name,
            hash_agent_token(data.agent_token)
        )
        db.commit()
    except IntegrityError as error:
        db.rollback()
        if isinstance(error.orig, UniqueViolation) and (
                error.orig.diag.constraint_name == "uq_devices_agent_token_hash"):
            raise AgentTokenAlreadyExistsError() from error
        raise
    except SQLAlchemyError as error:
        db.rollback()
        raise

    return new_device


def get_device_by_id(db: Session, device_id: int) -> Device | None:
    return get_device_record(db, device_id)


def get_devices(db: Session, limit: int = 10, offset: int = 0) -> list[Device]:
    return get_devices_record(db, limit, offset)


def get_device_by_token(db: Session, agent_token: str) -> Device | None:
    return get_device_by_token_hash_record(db, hash_agent_token(agent_token))
