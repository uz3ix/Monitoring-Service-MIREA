from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import HttpUrl
from app.modules.devices.exceptions import AgentTokenAlreadyExistsError
from app.modules.devices.schemas import DeviceCreate, DeviceResponse
from sqlalchemy.orm import Session
from app.modules.devices.models import Device
from app.db.session import get_db
from app.modules.devices.service import (
    create_device as create_device_service,
    get_device_by_id as get_device_service,
    get_devices as get_devices_service,
    get_device_by_token as get_devices_by_token_service
)

router = APIRouter()


@router.post("/devices",
             response_model=DeviceResponse,
             status_code=201, tags=["Device"])
def device_create(data: DeviceCreate, db: Session = Depends(get_db)) -> Device:
    try:
        new_device = create_device_service(db, data)
    except AgentTokenAlreadyExistsError:
        raise HTTPException(
            status_code=409,
            detail="Agent token already in use"
        )
    return new_device


@router.get("/devices/{device_id}",
            response_model=DeviceResponse,
            status_code=200,
            tags=["Device"])
def get_device_by_id(device_id: int, db: Session = Depends(get_db)) -> Device:
    device = get_device_service(db, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    return device


@router.get("/devices",
            response_model=list[DeviceResponse],
            status_code=200,
            tags=["Device"])
def get_devices(
        limit: int = Query(default=10, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        db: Session = Depends(get_db)) -> list[Device]:

    list_devices = get_devices_service(db, limit, offset)

    return list_devices


@router.get("/devices/token/{agent_token}",
            response_model=DeviceResponse,
            status_code=200,
            tags=["Device"])
def get_devices_by_token(
    agent_token: str,
    db: Session = Depends(get_db)
) -> Device | None:
    device = get_devices_by_token_service(db, agent_token)
    if device is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return device
