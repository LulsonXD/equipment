import secrets

from starlette import status
from starlette.responses import JSONResponse
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from models import *

app = FastAPI(redoc_url=None, title='Equipment API', description='API for equipment management', version='0.1.0')
security = HTTPBasic()

engine = create_async_engine(
    'postgresql+asyncpg://student:aq4BHZKJmZB414ywH8DYQ3Xda@helow19274.ru:5432/equipment',  # TODO: хранить не в коде
    future=True
)


def check_auth(credentials: HTTPBasicCredentials = Depends(security)):
    # TODO: хранить не в коде
    username_correct = secrets.compare_digest(credentials.username.encode('utf8'), b'5RNYBdLduTDxQCcM8YYrb5nA')
    password_correct = secrets.compare_digest(credentials.password.encode('utf8'), b'H4dScAyGbS89KgLgZBs2vPsk')

    if not username_correct or not password_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Basic'}
        )


async def get_session() -> AsyncSession:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


async def insert_entry(entry, session: AsyncSession):
    session.add(entry)
    await session.commit()
    await session.refresh(entry)
    return entry


async def insert_entries(entries, session: AsyncSession, refresh=True):
    session.add_all(entries)
    await session.commit()
    if refresh:
        for entry in entries:
            await session.refresh(entry)
    return entries


@app.exception_handler(DBAPIError)
async def database_error_handler(request, exc: DBAPIError):
    message = f'Error in statement: {exc.statement % exc.params}: {exc.orig}'
    return JSONResponse(
        status_code=400,
        content={'detail': [{'loc': ['body'], 'msg': message, 'type': 'database_error'}]},
    )


@app.post('/user', dependencies=[Depends(check_auth)], status_code=status.HTTP_201_CREATED)
async def create_user(user: UserInsert, session: AsyncSession = Depends(get_session)) -> User:
    user = User(**user.dict())
    return await insert_entry(user, session)


@app.post('/location', dependencies=[Depends(check_auth)], status_code=status.HTTP_201_CREATED)
async def create_location(location: LocationInsert, session: AsyncSession = Depends(get_session)) -> Location:
    location = Location(**location.dict())
    return await insert_entry(location, session)


@app.post('/hardware', dependencies=[Depends(check_auth)], status_code=status.HTTP_201_CREATED)
async def create_hardware(hardware: HardwareInsert, session: AsyncSession = Depends(get_session)) -> Hardware:
    hardware = Hardware(**hardware.dict())
    return await insert_entry(hardware, session)


@app.post('/terminal', dependencies=[Depends(check_auth)], status_code=status.HTTP_201_CREATED)
async def create_terminal(terminal: TerminalInsert, session: AsyncSession = Depends(get_session)) -> Terminal:
    terminal = Terminal(**terminal.dict())
    return await insert_entry(terminal, session)


@app.post('/rack', dependencies=[Depends(check_auth)], status_code=status.HTTP_201_CREATED)
async def create_rack(rack: RackInsert, session: AsyncSession = Depends(get_session)) -> Rack:
    rack = Rack(**rack.dict())
    return await insert_entry(rack, session)


@app.post('/stocks', dependencies=[Depends(check_auth)], status_code=status.HTTP_201_CREATED)
async def create_stock(stocks: list[StockInsert], session: AsyncSession = Depends(get_session)):
    stocks = [Stock(**stock.dict()) for stock in stocks]
    await insert_entries(stocks, session)
    return {'detail': 'OK'}


@app.post('/request', dependencies=[Depends(check_auth)], status_code=status.HTTP_201_CREATED)
async def create_request(request: RequestInsert, session: AsyncSession = Depends(get_session)) -> Request:
    hardware = request.hardware.copy()

    del request.hardware
    request = Request(**request.dict())
    session.add(request)
    await session.commit()
    await session.refresh(request)

    entries = [RequestHardware(request=request.id, hardware=item.hardware, count=item.count) for item in hardware]
    await insert_entries(entries, session, False)

    return request


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', host='0.0.0.0', port=8080)  # TODO: хранить не в коде
