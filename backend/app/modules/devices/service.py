from datetime import timedelta
from psycopg.errors import UniqueViolation
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import hash_agent_token
from app.core.time import retention_cutoff, utcnow
from app.modules.devices.exceptions import AgentTokenAlreadyExistsError
from app.modules.devices.models import Device
from app.modules.devices.repository import (
    get_device_by_token_hash as get_device_by_token_hash_record,
    create_device as create_device_record,
    get_device_by_id as get_device_record,
    update_device_name as update_device_name_record,
    get_devices as get_devices_record,
    get_device_for_update as get_device_for_update_record,
    get_filtered_devices as get_filtered_devices_record,
    rotate_agent_token as rotate_agent_token_record,
    delete_device as delete_device_record
)
from app.modules.devices.schemas import DeviceCreate, DeviceRename, DeviceResponse
from app.modules.metrics.repository import (
    get_latest_metrics as get_latest_metrics_record,
    get_latest_metrics_for_devices as get_latest_metrics_for_devices_record,
    delete_device_metrics as delete_device_metrics_record
)
from app.modules.metrics.schemas import MetricsResponse


def create_device(db: Session, data: DeviceCreate) -> Device:
    try:
        new_device = create_device_record(db, data.name, hash_agent_token(data.agent_token))
        db.commit()
    except IntegrityError as error:
        db.rollback()
        if isinstance(error.orig, UniqueViolation) and (error.orig.diag.constraint_name == "uq_devices_agent_token_hash"):
            raise AgentTokenAlreadyExistsError() from error
        raise
    except SQLAlchemyError:
        db.rollback()
        raise

    return new_device


def get_device_by_id(db: Session, device_id: int) -> Device | None:
    return get_device_record(db, device_id)


def get_devices(db: Session, limit: int = 10, offset: int = 0) -> list[Device]:
    return get_devices_record(db, limit, offset)


def get_device_by_token(db: Session, agent_token: str) -> Device | None:
    return get_device_by_token_hash_record(db, hash_agent_token(agent_token))


def update_device_name(db: Session, data: DeviceRename, device_id: int) -> Device | None:
    try:
        device = get_device_record(db, device_id)
        if device is None:
            return None
        device_new_name = update_device_name_record(db, device, data.name)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    return device_new_name


def device_view(db: Session, device: Device) -> DeviceResponse:
    view = DeviceResponse.model_validate(device)
    latest = get_latest_metrics_record(db, device.id, retention_cutoff())
    view.latest_metrics = MetricsResponse.model_validate(latest) if latest else None
    return view


def list_device_views(db: Session, limit: int, offset: int, search: str, status: str | None):
    threshold = utcnow() - timedelta(seconds=settings.online_timeout_seconds)
    devices, total = get_filtered_devices_record(db, limit, offset, search, status, threshold)
    ids = [device.id for device in devices]
    records = get_latest_metrics_for_devices_record(db, ids, retention_cutoff())
    latest = {record.device_id: record for record in records}
    views = []
    for device in devices:
        view = DeviceResponse.model_validate(device)
        metric = latest.get(device.id)
        view.latest_metrics = MetricsResponse.model_validate(metric) if metric else None
        views.append(view)
    return views, total


def rotate_agent_token(db: Session, device_id: int, token: str) -> Device | None:
    try:
        device = get_device_for_update_record(db, device_id)
        if device is None:
            return None
        rotate_agent_token_record(db, device, hash_agent_token(token))
        db.commit()
        return device
    except IntegrityError as error:
        db.rollback()
        if (isinstance(error.orig, UniqueViolation) and error.orig.diag.constraint_name == "uq_devices_agent_token_hash"):
            raise AgentTokenAlreadyExistsError() from error
        raise
    except SQLAlchemyError:
        db.rollback()
        raise


def delete_device(db: Session, device_id: int) -> bool:
    try:
        device = get_device_for_update_record(db, device_id)
        if device is None:
            return False
        delete_device_metrics_record(db, device_id)
        delete_device_record(db, device)
        db.commit()
        return True
    except SQLAlchemyError:
        db.rollback()
        raise
