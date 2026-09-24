from fastapi import FastAPI
from app.modules.health.router import router as health_router
from app.modules.devices.router import router as device_router

app = FastAPI(title="Мониторинговый сервис")

app.include_router(health_router)
app.include_router(device_router)
