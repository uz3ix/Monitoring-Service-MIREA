from datetime import datetime
from sqlalchemy import BigInteger, DateTime, Double, ForeignKey, Index, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Metrics(Base):
    __tablename__ = "metrics"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"))
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    cpu_percent: Mapped[float | None] = mapped_column(Double)
    memory_used_bytes: Mapped[int | None] = mapped_column(BigInteger)
    memory_total_bytes: Mapped[int | None] = mapped_column(BigInteger)
    disks: Mapped[list[dict[str, str | int]] | None] = mapped_column(JSONB(none_as_null=True), nullable=True)
    services: Mapped[dict[str, str] | None] = mapped_column(JSONB)

    __table_args__ = (
        Index("ix_metrics_device_collected_at", "device_id", "collected_at"),
        Index("ix_metrics_collected_at", "collected_at"),
    )
