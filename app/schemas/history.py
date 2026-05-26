from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AnalysisHistoryCreate(BaseModel):
    source: str = Field(max_length=32)
    product_url: str
    product_title: str | None = Field(default=None, max_length=512)
    product_price: str | None = Field(default=None, max_length=128)
    summary: str
    pros: list[str]
    cons: list[str]


class AnalysisHistoryPriceUpdate(BaseModel):
    product_price: str = Field(max_length=128)


class AnalysisHistoryRead(AnalysisHistoryCreate):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
