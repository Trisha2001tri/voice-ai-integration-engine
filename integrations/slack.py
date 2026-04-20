import os
import requests
from dotenv import load_dotenv

load_dotenv()

SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")


def send_to_slack(data):

    if not SLACK_WEBHOOK_URL:
        raise Exception("500|Missing webhook URL")

    payload = {
        "text": f"""
🚀 New Voice Lead

Name: {data['caller_name']}
Phone: {data['phone']}
Intent: {data['intent']}
Language: {data['language']}
Summary: {data['summary']}
"""
    }

    try:
        response = requests.post(
            SLACK_WEBHOOK_URL,
            json=payload,
            timeout=5
        )

        # If HTTP error like 404 / 500
        if response.status_code != 200:
            raise Exception(
                f"{response.status_code}|HTTP Error"
            )

        # Slack should return ok
        if response.text.strip().lower() != "ok":
            raise Exception(
                f"{response.status_code}|Invalid Slack Response"
            )

    except requests.exceptions.Timeout:
        raise Exception("408|Request Timeout")

    except requests.exceptions.ConnectionError:
        raise Exception("503|Connection Failed")

    except Exception as e:
        raise e