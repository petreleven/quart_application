from sqlalchemy import Column, Integer, String, JSON, Boolean
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from contextlib import asynccontextmanager

DATABASE_URL = "sqlite+aiosqlite:///./test.sqlite"
engine = create_async_engine(DATABASE_URL, future=True, echo=False)
async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "User"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    email = Column(String)
    reddit_token_id = Column(String)
    password = Column(String)
    config = Column(JSON)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)

    def json(self):
        return {"id": self.id, "email": self.email, "config": self.config}


class UserDAL:

    def __init__(self, db_session) -> None:
        self.db_session: AsyncSession = db_session

    async def create_user(
        self,
        name,
        email,
        reddit_token_id,
        password=None,
        config=None,
        is_active=True,
        is_admin=False,
    ):
        new_user = User(
            name=name,
            email=email,
            reddit_token_id=reddit_token_id,
            password=password,
            config=config,
            is_active=is_active,
            is_admin=is_admin,
        )
        self.db_session.add(new_user)
        await self.db_session.flush()
        return new_user.json()

    async def get_all_users(self):
        query_result = await self.db_session.execute(select(User).order_by(User.id))
        return {"users": [user.json() for user in query_result.scalars().all()]}

    async def get_user(self, user_id):
        query = select(User).where(User.id == user_id)
        try:
            query_result = await self.db_session.execute(query)
            user = query_result.one()
            return user[0].json()
        except NoResultFound:
            return {"Users": None}

    async def get_user_by_name(self, name):
        query = select(User).where(User.name == name)
        try:
            query_result = await self.db_session.execute(query)
            user = query_result.one()
            return user[0].json()
        except NoResultFound:
            return {"Users": None}

    async def get_users_with_token(self):
        query = select(User).where(User.reddit_token_id != None)
        return await self.db_session.execute(query)


@asynccontextmanager
async def user_dal():
    async with async_session() as session:
        async with session.begin():
            yield UserDAL(session)
