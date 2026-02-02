# OrianaSurvey123Emailer

Deployed to Caprover at https://survey123-webhooks.server.hakai.app/

Provides a single POST endpoint for emailing a single user when Survery123 data is submitted.

## WHY

Oriana Smy wanted to receive emails notifications when people submit her survey on Survey123.

## Setup in Caprover

The following env variables need to be defined:

- "SENDER_EMAIL": Email to send from the Google SMTP server (e.g. notifications@hakai.org)
- "SENDER_APP_PASSWORD": App password for the sender email (e.g "1234 abcd wxyz 9876")
- "RECEIVER_EMAIL": Email to send notifications to (e.g. taylor.denouden@hakai.org)

I just deployed with the Caprover CLI since it's not expected this will every need to change.

## Setup in Survey123

Follow these steps:

1. Navigate to the Survey123 settings for your form.
2. Locate the webhook settings.
3. Add a new webhook with the URL `https://survey123-webhooks.server.hakai.app/survey123_email_oriana`.
4. Configure the webhook to trigger on form submission.
5. Check the "Survey Info", "User Info", and "Portal Info".
5. Save the changes.