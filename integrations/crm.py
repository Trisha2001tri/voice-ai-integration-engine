import os
import requests
from dotenv import load_dotenv

load_dotenv()


def send_to_crm(data):
    subdomain = os.getenv("ZENDESK_SUBDOMAIN")
    email = os.getenv("ZENDESK_EMAIL")
    token = os.getenv("ZENDESK_API_TOKEN")

    url = f"https://{subdomain}.zendesk.com/api/v2/tickets.json"

    payload = {
        "ticket": {
            "subject": f"Voice Lead - {data['intent']}",
            "comment": {
                "body": f"""
Caller Name: {data['caller_name']}
Phone: {data['phone']}
Language: {data['language']}
Summary: {data['summary']}
"""
            },
            "priority": "normal"
        }
    }

    response = requests.post(
        url,
        json=payload,
        auth=(f"{email}/token", token),
        timeout=5
    )

    response.raise_for_status()

    return response.json()