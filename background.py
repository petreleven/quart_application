from celery import Celery
from models import user_dal
from asgiref.sync import async_to_sync
import asyncio

celery_app = Celery("tasks", broker="amqp://localhost")


async def fetch_messages(reddit_token_id: str):
    "check if bot is mentioned"
    print(reddit_token_id)
    pass


async def post_to_reddit():
    "send acknowledgement"
    pass


async def message_towards_bot_async():
    async with user_dal() as ud:
        query_results = await ud.get_users_with_token()
        for user in query_results:
            user_obj = user[0]
            await asyncio.sleep(8)
            message: bool = await fetch_messages(reddit_token_id=user_obj.reddit_token_id)
            if message:
                await post_to_reddit()


@celery_app.task
def do_message_tasks():
    async_to_sync(message_towards_bot_async)()


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(2.0, do_message_tasks, name="****fetch_messages****", expires=30)
