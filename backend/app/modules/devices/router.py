from fastapi import APIRouter, Depends, HTTPException, Query
from app.modules.devices.service import create_device as create_device_service, get_device_by_id as get_device_service, get_devices as get_devices_service
from app.modules.devices.schemas import DeviceCreate, DeviceResponse
from sqlalchemy.orm import Session
from app.modules.devices.models import Device
from app.db.session import get_db

router = APIRouter()


@router.post("/devices", response_model=DeviceResponse, status_code=201)
def device_create(data: DeviceCreate, db: Session = Depends(get_db)) -> Device:
    new_device = create_device_service(db, data)
    return new_device


@router.get("/devices/{device_id}",
            response_model=DeviceResponse,
            status_code=200)
def get_device_by_id(device_id: int, db: Session = Depends(get_db)) -> Device:
    device = get_device_service(db, device_id)
    if device is None:
        raise HTTPException(status_code=404, detail="Device not found")

    return device


@router.get("/devices", response_model=list[DeviceResponse], status_code=200)
def get_devices(
        limit: int = Query(default=10, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
        db: Session = Depends(get_db)) -> list[Device]:

    list_devices = get_devices_service(db, limit, offset)

    return list_devices
