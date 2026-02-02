from datetime import datetime
from email.message import EmailMessage
from functools import lru_cache
from typing import Literal
from zoneinfo import ZoneInfo

import aiosmtplib
from fastapi import FastAPI, Depends
from loguru import logger
from pydantic import BaseModel, ConfigDict, EmailStr
from pydantic_settings import BaseSettings

app = FastAPI(
    title="Email Notifier API",
    description="Web hooks for Survey123",
    version="1.0.0",
)


class PortalInfo(BaseModel):
    url: str
    token: str


class SurveyInfo(BaseModel):
    formItemId: str
    formTitle: str
    serviceItemId: str
    serviceUrl: str


class UserInfo(BaseModel):
    username: str
    firstName: str
    lastName: str
    fullName: str
    email: str


class EventPayload(BaseModel):
    eventType: Literal["addData", "editData"]
    portalInfo: PortalInfo
    surveyInfo: SurveyInfo
    userInfo: UserInfo

    model_config = ConfigDict(extra="allow")


class SuccessResponse(BaseModel):
    success: bool
    details: str | None = None


class Settings(BaseSettings):
    # These values are loaded from env variables
    sender_email: EmailStr
    sender_app_password: str
    receiver_email: EmailStr
    tz: str = "America/Vancouver"
    email_host: str = "smtp.gmail.com"
    email_port: int = 465


@lru_cache(maxsize=1)
def get_settings():
    return Settings()


@app.post("/survey123_email_oriana", tags=["webhook"])
async def survey123_email_oriana(
        payload: EventPayload, settings: Settings = Depends(get_settings)
) -> SuccessResponse:
    now = datetime.now(tz=ZoneInfo(settings.tz))
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    form_title = payload.surveyInfo.formTitle
    user = payload.userInfo

    msg = EmailMessage()
    msg["Subject"] = f"New data added to {form_title} by {user.fullName}"
    msg["From"] = settings.sender_email
    msg["To"] = settings.receiver_email
    msg.set_content(
        f"New data added to {form_title} by {user.fullName} ({user.email}) at {timestamp}."
    )

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.email_host,
            port=settings.email_port,
            username=settings.sender_email,
            password=settings.sender_app_password,
            use_tls=True,
        )
        logger.info("Email sent successfully!")
        return SuccessResponse(success=True)
    except Exception:
        logger.exception("Error sending email")
        return SuccessResponse(success=False, details="Email sending failed.")
