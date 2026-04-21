# OrianaSurvey123Emailer

A FastAPI application that receives Survey123 webhook events and sends email notifications
when a survey is submitted.

## How it works

Survey123 sends a POST request to this service whenever a new record is submitted. The service
extracts the submitter's name and email from the survey data and sends an email notification to
the configured recipient.

The webhook endpoint is: `POST /survey123_email_oriana`

## Environment Variables

The following environment variables must be set before running the application.

### Required

- `SENDER_EMAIL` — Gmail address used to send notification emails (e.g. `notifications@example.com`)
- `SENDER_APP_PASSWORD` — [Google App Password][app-pw] for the sender account, not your regular
  Gmail password (e.g. `abcd efgh ijkl mnop`)
- `RECEIVER_EMAIL` — Email address that receives the notifications (e.g. `recipient@example.com`)

[app-pw]: https://support.google.com/accounts/answer/185833

> **Note on Google App Passwords:** 2-Step Verification must be enabled on the sender Google
> account before you can create an App Password. Visit
> [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords) to generate one.

### Optional

- `TZ` — Timezone for timestamps in notification emails (default: `America/Vancouver`)
- `EMAIL_HOST` — SMTP server hostname (default: `smtp.gmail.com`)
- `EMAIL_PORT` — SMTP server port using SSL (default: `465`)

## Survey123 Webhook Setup

1. Open your survey in [Survey123](https://survey123.arcgis.com) and go to **Settings > Webhooks**.
2. Click **Add webhook**.
3. Fill in the form:
   - **Name:** `Submission email` (or any descriptive name)
   - **Payload URL:** The URL of your deployed service followed by the endpoint path, e.g.
     `https://your-server.example.com/survey123_email_oriana`
4. Under **Trigger events**, check only:
   - [x] New record submitted
5. Under **Event data**, check only:
   - [x] Survey info
   - [x] Submitted record
6. Click **Save**.

> **Survey field names:** The application reads `observer_name` and `email_address` from the
> submitted record's attributes. Ensure your Survey123 form uses these exact field names, or
> update `main.py` to match your form's field names.

## Deployment

This application is packaged as a Docker image (see `Dockerfile`) and can be deployed anywhere
Docker containers are supported. For general FastAPI deployment guidance, see the
[FastAPI deployment documentation](https://fastapi.tiangolo.com/deployment/).

The container listens on port `8000` and is started with:

```
uvicorn main:app --host 0.0.0.0 --port 8000
```

Pass the required environment variables to the container at runtime (e.g. via `-e` flags,
a `.env` file, or your platform's secrets manager).