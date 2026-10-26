from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class Meter(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    meter_id: str = Field(alias="meterId")
    serial_no: str = Field(alias="serialNo")
    make: str
    phase_type: str = Field(alias="phaseType")
    install_status: str = Field(alias="installStatus")
    dt_code: str = Field(alias="dtCode")


class MeterListResponse(BaseModel):
    data: list[Meter]
    total: int
    page: int
    page_size: int = Field(alias="pageSize")


class ConsumptionReading(BaseModel):
    timestamp: datetime
    kwh: float
    kvah: float
    volt_r: float = Field(alias="voltR")


class ConsumptionResponse(BaseModel):
    data: list[ConsumptionReading]


class HealthResponse(BaseModel):
    status: str
    portal: str
