from datetime import datetime
from typing import List, Optional, Tuple
from pydantic import BaseModel, field_validator

from app.src.router.response import BaseListResponse, BaseResponse


class CustomerHistoryBaseSchema(BaseModel):
    customer_no: str
    customer_name: Optional[str] = None
    visit_date: str
    relationship_type: str
    contact_name: Optional[str] = None
    address_status: str
    address: Optional[str] = None
    sub_district: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    zip_code: Optional[str] = None
    geopoint: Optional[Tuple[float, float]] = None
    phone_number_status: str
    phone_number: Optional[str] = None
    mobile_phone_status: str
    mobile_phone: Optional[str] = None
    remark: Optional[str] = None

    @field_validator("visit_date")
    @classmethod
    def validate_visit_date(cls, value):
        try:
            value = value.replace("T", " ")
            datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except ValueError as exc:
            raise ValueError(
                "visit_date must be in the format 'YYYY-MM-DD HH:MM:SS'") from exc
        return value

    @field_validator("sub_district")
    @classmethod
    def validate_sub_district(cls, value):
        if value:
            return value.upper()
        return value

    @field_validator("district")
    @classmethod
    def validate_district(cls, value):
        if value:
            return value.upper()
        return value

    @field_validator("city")
    @classmethod
    def validate_city(cls, value):
        if value:
            return value.upper()
        return value
    
    @field_validator("province")
    @classmethod
    def validate_province(cls, value):
        if value:
            return value.upper()
        return value

    @field_validator("zip_code")
    @classmethod
    def validate_zip_code(cls, value):
        if value and len(value) > 5:
            raise ValueError("zip_code must be 5 digits")
        return value


class CustomerHistoryListSchema(CustomerHistoryBaseSchema):
    id: int
    created_at: str
    updated_by: Optional[str] = None


class CustomerHistoryCreateSchema(CustomerHistoryBaseSchema):
    followup_session_id: Optional[int] = None
    fc_id: Optional[int] = None
    updated_by: Optional[str] = None
    attachment_id1: Optional[str] = None
    attachment_id2: Optional[str] = None


class CustomerHistoryDetailSchema(CustomerHistoryCreateSchema):
    id: int
    attachment_id1: str | None
    attachment_id2: str | None


class CustomerHistoryDetailResponse(BaseResponse):
    data: Optional[CustomerHistoryDetailSchema] = None


class CustomerHistoryListResponse(BaseListResponse):
    data: List[CustomerHistoryListSchema] = []
