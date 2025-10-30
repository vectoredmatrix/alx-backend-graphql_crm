from celery import shared_task
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime

@shared_task
def generate_crm_report():
    """
    Generates a weekly CRM report via GraphQL and logs results.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "/tmp/crm_report_log.txt"

    try:
        # Set up GraphQL client
        transport = RequestsHTTPTransport(
            url="http://localhost:8000/graphql",
            verify=True,
            retries=3,
        )
        client = Client(transport=transport, fetch_schema_from_transport=False)

        # GraphQL query to summarize data
        query = gql("""
        {
          allCustomers {
            totalCount
          }
          allOrders {
            totalCount
            edges {
              node {
                totalAmount
              }
            }
          }
        }
        """)

        result = client.execute(query)
        customers = result.get("allCustomers", {}).get("totalCount", 0)
        orders_data = result.get("allOrders", {})
        orders = orders_data.get("totalCount", 0)

        # Compute total revenue
        total_revenue = 0
        for edge in orders_data.get("edges", []):
            node = edge.get("node", {})
            total_revenue += float(node.get("totalAmount", 0))

        # Log the summary
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - Report: {customers} customers, {orders} orders, {total_revenue:.2f} revenue\n")

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - Error generating CRM report: {e}\n")
