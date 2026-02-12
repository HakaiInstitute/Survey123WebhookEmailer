import json
from datetime import datetime
from email.message import EmailMessage
from functools import lru_cache
from typing import Literal
from zoneinfo import ZoneInfo

import aiosmtplib
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel, ConfigDict, EmailStr
from pydantic_settings import BaseSettings

app = FastAPI(
    title="Email Notifier API",
    description="Web hooks for Survey123",
    version="1.0.0",
)
origins = [
    "https://survey123.arcgis.com",
    "http://localhost",
    "http://localhost:8000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PortalInfo(BaseModel):
    url: str | None = None
    token: str | None = None

    model_config = ConfigDict(extra="allow")


class SurveyInfo(BaseModel):
    formItemId: str | None = None
    formTitle: str | None = None
    serviceItemId: str | None = None
    serviceUrl: str | None = None

    model_config = ConfigDict(extra="allow")


class UserInfo(BaseModel):
    username: str | None = None
    firstName: str | None = None
    lastName: str | None = None
    fullName: str | None = None
    email: str | None = None

    model_config = ConfigDict(extra="allow")


class EventPayload(BaseModel):
    eventType: Literal["addData", "editData"]
    portalInfo: PortalInfo | None = None
    surveyInfo: SurveyInfo | None = None
    userInfo: UserInfo | None = None
    feature: dict = dict()

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
    form_title = payload.surveyInfo.formTitle if payload.surveyInfo else "Unknown Survey"

    logger.info(json.dumps(payload.feature))

    attributes = payload.feature.get("attributes", {})
    submitted_email = attributes.get("email_addr", "Unknown")
    submitted_name = attributes.get("observer_n", "Unknown")

    msg = EmailMessage()
    msg["Subject"] = f"New data added to {form_title} by {submitted_name}"
    msg["From"] = settings.sender_email
    msg["To"] = settings.receiver_email
    msg.set_content(
        f"New data added to {form_title} by {submitted_name} ({submitted_email}) at {timestamp}."
    )

    try:
        await aiosmtplib.send(
            msg,
            hostname=settings.email_host,
            port=settings.email_port,
            username=str(settings.sender_email),
            password=settings.sender_app_password,
            use_tls=True,
        )
        logger.info("Email sent successfully!")
        return SuccessResponse(success=True)
    except Exception:
        logger.exception("Error sending email")
        return SuccessResponse(success=False, details="Email sending failed.")
