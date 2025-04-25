from sqlalchemy import select
from database.models import User, async_session


async def add_user_if_not_exists(user_id: int, username: str):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            session.add(User(id=user_id, tg_username=username or "no_username"))
            await session.commit()
