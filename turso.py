from sqlalchemy import Column, Integer, String, JSON, Boolean, MetaData
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from contextlib import asynccontextmanager
import libsql_client
import asyncio


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
    def __init__(self, client) -> None:
        self.client = client

    async def create_user(self, name, email, reddit_token_id, password=None, config=None, is_active=True, is_admin=False):
        new_user = User(name=name, email=email, reddit_token_id=reddit_token_id, password=password,
                        config=config, is_active=is_active, is_admin=is_admin)
        self.client.add(new_user)
        await self.client.flush()
        return new_user.json()

    async def get_all_users(self):  # -> dict[str, list]:
        query_result = await self.client.execute(select(User).order_by(User.id))
        return {"users": [user.json() for user in query_result.scalars().all()]}

    async def get_user(self, user_id):
        query = select(User).where(User.id == user_id)
        try:
            query_result = await self.client.execute(query)
            user = query_result.one()
            return user[0].json()
        except NoResultFound:
            return {"Users": None}


auth_token = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJpYXQiOiIyMDIzLTExLTAzVDE3OjE3OjE0LjE4OTk0MjU2NVoiLCJpZCI6ImE0YjQzMDA5LTc5YmEtMTFlZS1iNzEyLTdhZWJhMmI3ZmVhYiJ9.pEpciQqyIYga3AT7ojGPbRM8GcpujVwznUvVj_mvIkGrUnjLvGCXuCH_9lyNOGf8SI1Xenqoxc8p-BerEIeXBw"
url = "strong-bushwacker-petreleven.turso.io"


async def start():
    client = libsql_client.create_client(
        url=f"libsql://{url}",
        auth_token=auth_token)
    client.execute(
        "create table example_users ( uid text primary key, email text);")


async def s2():
    url1 = f"sqlite+libsql://{url}/?authToken={auth_token}&secure=false"
    engine = create_async_engine(url1)


if __name__ == "__main__":
    l = asyncio.get_event_loop()
    l.run_until_complete(s2())
