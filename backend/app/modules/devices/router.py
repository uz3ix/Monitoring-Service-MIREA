from typing import Literal
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.modules.auth.dependencies import current_agent, current_user
from app.modules.devices.service import (
    create_device as create_device_service,
    list_device_views as list_device_views_service,
    get_device_by_id as get_device_by_id_service,
    device_view as device_view_service,
    update_device_name as update_device_name_service,
    rotate_agent_token as rotate_agent_token_service,
    delete_device as delete_device_service
)
from app.modules.devices.models import Device
from app.modules.devices.schemas import AgentTokenUpdate, DeviceCreate, DeviceRename, DeviceResponse

router = APIRouter(tags=["Device"])
admin = [Depends(current_user)]


@router.post("/devices", response_model=DeviceResponse, status_code=201, dependencies=admin)
def device_create(data: DeviceCreate, db: Session = Depends(get_db)):
    return create_device_service(db, data)


@router.get("/devices", response_model=list[DeviceResponse], dependencies=admin)
def get_devices(response: Response,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: str = Query("", max_length=100),
    status: Literal["online", "offline"] | None = None,
    db: Session = Depends(get_db),
):
    devices, total = list_device_views_service(db, limit, offset, search, status)
    response.headers["X-Total-Count"] = str(total)
    return devices


@router.get("/devices/{device_id}", response_model=DeviceResponse, dependencies=admin)
def get_device_by_id(device_id: int, db: Session = Depends(get_db)):
    device = get_device_by_id_service(db, device_id)
    if device is None:
        raise HTTPException(404, "Device not found")
    return device_view_service(db, device)


@router.get("/agent", response_model=DeviceResponse)
def agent_identity(device: Device = Depends(current_agent)):
    return device


@router.patch("/devices/{device_id}", response_model=DeviceResponse, dependencies=admin)
def update_device_name(device_id: int, data: DeviceRename, db: Session = Depends(get_db)):
    device = update_device_name_service(db, data, device_id)
    if device is None:
        raise HTTPException(404, "Device not found")
    return device_view_service(db, device)


@router.put("/devices/{device_id}/agent-token", response_model=DeviceResponse, dependencies=admin)
def rotate_token(device_id: int, data: AgentTokenUpdate, db: Session = Depends(get_db)):
    device = rotate_agent_token_service(db, device_id, data.agent_token)
    if device is None:
        raise HTTPException(404, "Device not found")
    return device_view_service(db, device)


@router.delete("/devices/{device_id}", status_code=204, dependencies=admin)
def delete_device(device_id: int, db: Session = Depends(get_db)):
    if not delete_device_service(db, device_id):
        raise HTTPException(404, "Device not found")
    return Response(status_code=204)
