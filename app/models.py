from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TicketResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    category: Literal["billing", "technical", "account", "other"]
    priority: int = Field(ge=1, le=5)
    summary: str = Field(min_length=1, max_length=500)
    needs_human: bool


class CustomerPlanArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str = Field(min_length=1)


class CustomerPlanResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str
    plan: str
    active: bool
