from celery import Celery
from asgiref.sync import async_to_sync
from fastapi_mail import ConnectionConfig, FastMail
from app.config import db_settings,notification_settings
from app.utils import TEMPLATE_DIR

FastMail(
            ConnectionConfig(
                **notification_settings.model_dump(),
                TEMPLATE_FOLDER=TEMPLATE_DIR
            )
        )
send_message = async_to_sync(FastMail.send_message)


app = Celery(
    "api_tasks",
    broker=db_settings.REDIS_URL(9),
    backend=db_settings.REDIS_URL(9)
)

@app.task
def send_mail(
    recipients:list[str],
    subject:str,
    body:str,
):
    send_message(
        recipients = recipients,
        subject = subject,
        body= body
    )
    return "message sent!"
