from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Bron


async def orm_bron(session: AsyncSession, data: dict):
    session.add(Bron(
    name=data["name"],
    phone_number=data["phone_number"],
    place=data["place"],
    date=data["date"],
    time=data["time"]
))
    await session.commit()

