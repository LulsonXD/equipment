import datetime
import phonenumbers
from enum import Enum

from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from pydantic import EmailStr, validator, HttpUrl, BaseModel


class UserType(str, Enum):
    user = 'user'
    admin = 'admin'


class HardwareType(str, Enum):
    PLD = 'PLD'
    other = 'other'


class RequestStatus(str, Enum):
    new = 'new'
    taken = 'taken'
    completed = 'completed'
    canceled = 'canceled'


class HardwareInRequest(BaseModel):
    hardware: int
    count: int


class UserInsert(SQLModel):
    active: bool = True
    type: UserType = Field(sa_column=Column(ENUM(UserType), nullable=False), default=UserType.user)
    first_name: str = None
    last_name: str = None
    patronymic: str = None
    image_link: HttpUrl = None
    email: EmailStr = Field(unique=True)
    phone: str = None
    card_id: str = None
    card_key: str = None
    comment: str = ''

    @validator('phone')
    def phone_validator(cls, v):
        if not v:
            return v
        try:
            number = phonenumbers.parse(v, 'RU')
        except phonenumbers.phonenumberutil.NumberParseException:
            raise ValueError('Phone number is not valid')
        if not phonenumbers.is_valid_number(number):
            raise ValueError('Phone number is not valid')
        return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)


class LocationInsert(SQLModel):
    name: str = Field(min_length=1, unique=True)
    width: int = Field(ge=1)
    height: int = Field(ge=1)


class TerminalInsert(SQLModel):
    name: str = Field(primary_key=True)
    location: int = Field(foreign_key='location.id')
    x: int = Field(ge=0)
    y: int = Field(ge=0)


class HardwareInsert(SQLModel):
    name: str = Field(min_length=1, unique=True)
    type: HardwareType = Field(sa_column=Column(ENUM(HardwareType), nullable=False), default=HardwareType.other)
    description: str = ''
    image_link: HttpUrl = None
    specifications: dict[str, int | float | str] = Field(sa_column=Column(JSONB, nullable=False), default={})


class RackInsert(SQLModel):
    location: int = Field(foreign_key='location.id')
    width: int = Field(ge=0)
    height: int = Field(ge=0)
    x: int = Field(ge=0)
    y: int = Field(ge=0)


class StockInsert(SQLModel):
    hardware: int = Field(primary_key=True, foreign_key='hardware.id')
    rack: int = Field(primary_key=True, foreign_key='rack.id')
    rack_position: int = Field(primary_key=True, ge=1, le=9)
    count: int = Field(ge=0)


class RequestBase(SQLModel):
    user: int = Field(foreign_key='user.id')
    location: int = Field(foreign_key='location.id')
    status: RequestStatus = Field(sa_column=Column(ENUM(RequestStatus), nullable=False, default=RequestStatus.new))
    comment: str = ''
    taken_date: datetime.datetime = None
    return_date: datetime.datetime = None
    issued_by: int = Field(foreign_key='user.id', nullable=True, default=None)


class RequestInsert(RequestBase):
    hardware: list[HardwareInRequest]
