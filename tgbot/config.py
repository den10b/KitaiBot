import os
from dataclasses import dataclass

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from environs import Env


@dataclass
class DbConfig:
    host: str
    password: str
    user: str
    database: str
    port: str


@dataclass
class TgBot:
    token: str
    admin_ids: list
    use_redis: bool


@dataclass
class Miscellaneous:
    time_zone: str
    admin_email: str
    scheduler: AsyncIOScheduler


@dataclass
class Config:
    tg_bot: TgBot
    db: DbConfig
    misc: Miscellaneous


def load_config(path: str = None):
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            admin_ids=list(map(int, env.list("ADMINS"))),
            use_redis=env.bool("USE_REDIS"),
        ),
        db=DbConfig(
            host=env.str('DB_HOST'),
            password=env.str('DB_PASS'),
            user=env.str('DB_USER'),
            database=env.str('DB_NAME'),
            port=env.str('DB_PORT')
        ),
        misc=Miscellaneous(
            time_zone=env.str('TIME_ZONE'),
            admin_email=env.str('ADMIN_EMAIL'),
            scheduler=AsyncIOScheduler(timezone=env.str('TIME_ZONE'))
        )
    )


# def setup_django():
#     os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_panel.settings')
#     os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
#     django.setup()
