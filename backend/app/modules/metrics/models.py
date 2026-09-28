from datetime import datetime
from app.db.base import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Double, ForeignKey, BigInteger, DateTime, func, Index
from sqlalchemy.dialects.postgresql import JSONB


class Metrics(Base):
    __tablename__ = "metrics"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"))
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    cpu_percent: Mapped[float | None] = mapped_column(Double)
    memory_used_bytes: Mapped[int | None] = mapped_column(BigInteger)
    memory_total_bytes: Mapped[int | None] = mapped_column(BigInteger)
    disk_used_bytes: Mapped[int | None] = mapped_column(BigInteger)
    disk_total_bytes: Mapped[int | None] = mapped_column(BigInteger)
    services: Mapped[dict[str, str] | None] = mapped_column(JSONB)

    __table_args__ = (
        Index("ix_metrics_device_collected_at", "device_id", "collected_at"),
    )