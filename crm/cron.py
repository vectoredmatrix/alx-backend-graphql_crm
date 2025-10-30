import datetime
import requests

def log_crm_heartbeat():
    """
    Logs a heartbeat message every 5 minutes to verify CRM health.
    Optionally checks the GraphQL endpoint for responsiveness.
    """
    timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"

    log_file = "/tmp/crm_heartbeat_log.txt"

    # Optional GraphQL health check
    try:
        response = requests.post(
            "http://localhost:8000/graphql",
            json={"query": "{ __typename }"},  # lightweight introspection query
            timeout=5
        )
        if response.status_code == 200:
            message += " - GraphQL OK"
        else:
            message += f" - GraphQL Error {response.status_code}"
    except Exception as e:
        message += f" - GraphQL Unreachable ({e})"

    # Append to log file
    with open(log_file, "a") as f:
        f.write(message + "\n")
