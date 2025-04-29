from datetime import datetime, time
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Bron
from datetime import date, time

async def orm_bron(
    session: AsyncSession, 
    username: str | None,
    place: str, 
    minkoms: str,
    name: str, 
    phone_number: str, 
    date: date, 
    time: time,
    timeout: time,
    pupils: str,
    contact_method: str
):
    session.add(Bron(
        place=place,
        minkoms=minkoms,
        username=username,
        name=name,
        phone_number=phone_number,
        date=date,
        time=time,
        timeout=timeout,
        pupils=pupils,
        contact_method=contact_method 
    ))
    await session.commit()