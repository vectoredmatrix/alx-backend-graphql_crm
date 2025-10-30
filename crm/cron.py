from datetime import datetime
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def update_low_stock():
    """
    Cron job that calls the GraphQL mutation to restock low-stock products
    and logs the updates.
    """
    timestamp = datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
    log_file = "/tmp/low_stock_updates_log.txt"

    try:
        # Set up GraphQL client
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)

        # Mutation to update low-stock products
        mutation = gql("""
        mutation {
          updateLowStockProducts {
            message
            updatedProducts {
              name
              stock
            }
          }
        }
        """)

        result = client.execute(mutation)
        data = result.get("updateLowStockProducts", {})
        message = data.get("message", "No message")
        products = data.get("updatedProducts", [])

        # Log results
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
            for p in products:
                f.write(f"    - {p['name']}: stock now {p['stock']}\n")

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"[{timestamp}] Error updating low-stock products: {e}\n")
