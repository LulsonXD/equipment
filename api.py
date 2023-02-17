from sqlalchemy import DateTime, func
from sqlalchemy import types as sqltypes

from .insert import *


class SERIAL(sqltypes.UserDefinedType):
    def get_col_spec(self, **kw):
        return 'SERIAL'


class User(UserInsert, table=True):
    id: int = Field(primary_key=True)
    created: datetime.datetime = Field(sa_column=Column(DateTime, server_default=func.now(), nullable=False))


class Location(LocationInsert, table=True):
    id: int = Field(primary_key=True)
    created: datetime.datetime = Field(sa_column=Column(DateTime, server_default=func.now(), nullable=False))


class Terminal(TerminalInsert, table=True):
    created: datetime.datetime = Field(sa_column=Column(DateTime, server_default=func.now(), nullable=False))


class Hardware(HardwareInsert, table=True):
    id: int = Field(primary_key=True)
    created: datetime.datetime = Field(sa_column=Column(DateTime, server_default=func.now(), nullable=False))


class Rack(RackInsert, table=True):
    id: int = Field(primary_key=True)


class Stock(StockInsert, table=True):
    id: int = Field(sa_column=Column(SERIAL, unique=True, server_default=func.nextval('stock_id_seq'), nullable=False))


class Request(RequestBase, table=True):
    id: int = Field(primary_key=True)
    created: datetime.datetime = Field(sa_column=Column(DateTime, server_default=func.now(), nullable=False))


class RequestHardware(SQLModel, table=True):
    request: int = Field(primary_key=True, foreign_key=Request.id)
    hardware: int = Field(primary_key=True, foreign_key=Hardware.id)
    stock: int = Field(foreign_key=Stock.id)
    count: int = Field(ge=1)
