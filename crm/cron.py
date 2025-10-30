from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def log_crm_heartbeat():
    """
    Logs a heartbeat message every 5 minutes to verify CRM health.
    Optionally queries the GraphQL 'hello' field to confirm responsiveness.
    """
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    message = f"{timestamp} CRM is alive"
    log_file = "/tmp/crm_heartbeat_log.txt"

    # Optional GraphQL endpoint health check using gql
    try:
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)

        # Query a simple field like `hello` to test the GraphQL endpoint
        query = gql("{ hello }")
        result = client.execute(query)
        hello_response = result.get("hello", "No response")

        message += f" - GraphQL OK ({hello_response})"

    except Exception as e:
        message += f" - GraphQL Error ({e})"

    # Append heartbeat log
    with open(log_file, "a") as f:
        f.write(message + "\n")
