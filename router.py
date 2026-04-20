import json
import os
import time
import uuid
from datetime import datetime

from integrations.slack import send_to_slack
from integrations.crm import send_to_crm


def load_config():
    with open("config.json", "r") as f:
        return json.load(f)


def log_failure(event, destination, retry_count, error, error_code=None):
    failure_entry = {
        "event_id": str(uuid.uuid4()),
        "time": str(datetime.now()),
        "caller_name": event["caller_name"],
        "intent": event["intent"],
        "destination": destination,
        "status": "failed",
        "retry_count": retry_count,
        "error_message": error,
        "error_code": error_code
    }

    with open("failures.log", "a") as f:
        f.write(json.dumps(failure_entry) + "\n")


def save_log(
    event,
    destination,
    status,
    retry_count=0,
    error_message=None,
    error_code=None
):
    log_entry = {
        "event_id": str(uuid.uuid4()),
        "time": str(datetime.now()),
        "caller_name": event["caller_name"],
        "intent": event["intent"],
        "destination": destination,
        "status": status,
        "retry_count": retry_count,
        "error_message": error_message,
        "error_code": error_code
    }

    logs = []

    if os.path.exists("logs.json"):
        with open("logs.json", "r") as f:
            try:
                logs = json.load(f)
            except:
                logs = []

    logs.append(log_entry)

    with open("logs.json", "w") as f:
        json.dump(logs, f, indent=4)


def route_event(event):
    config = load_config()
    intent = event.get("intent")

    if intent not in config:
        return "No matching route found"

    action = config[intent]["action"]

    if action == "slack":
        last_error = None
        error_code = None

        for attempt in range(3):
            try:
                send_to_slack(event)

                save_log(
                    event,
                    "slack",
                    "success",
                    retry_count=attempt
                )

                return "Sent to Slack"

            except Exception as e:
                raw_error = str(e)

                if "|" in raw_error:
                    error_code, last_error = raw_error.split("|", 1)
                else:
                    error_code = "UNKNOWN"
                    last_error = raw_error

                print(f"Retry {attempt + 1} failed: {raw_error}")
                time.sleep(1)

        save_log(
            event,
            "slack",
            "failed",
            retry_count=3,
            error_message=last_error,
            error_code=error_code
        )

        log_failure(
            event,
            "slack",
            3,
            last_error,
            error_code
        )

        return "Slack failed after retries"

    elif action == "crm":
        send_to_crm(event)

        save_log(
            event,
            "crm",
            "success",
            retry_count=0
        )

        return "Sent to CRM"

    else:
        return "Unknown action"