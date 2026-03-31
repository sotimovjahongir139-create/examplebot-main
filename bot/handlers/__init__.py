from aiogram import Dispatcher, Router

from bot.handlers.common import router as common_router


def get_routers() -> list[Router]:
    return [common_router]


def register_routers(dispatcher: Dispatcher) -> None:
    for router in get_routers():
        dispatcher.include_router(router)

