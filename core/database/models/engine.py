from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from loader import DBSettings

import docker

client_ = docker.from_env()
print(client_.containers.get('auto_quiz').attrs['NetworkSettings']['IPAddress'])
container = client_.containers.get('auto_quiz')
container_ip = container.attrs['NetworkSettings']['IPAddress']

# Определение базы данных
# DATABASE_URL = f"postgresql+asyncpg:///auto_quiz"
DATABASE_URL = f"postgresql+asyncpg://{DBSettings.POSTGRES_USER}:{DBSettings.POSTGRES_PASSWORD}@{container_ip}:{DBSettings.DB_PORT}/auto_quiz"
print(DATABASE_URL)
engine = create_async_engine(DATABASE_URL, echo=False)

async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


