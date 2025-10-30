from celery import shared_task
from datetime import datetime
import requests  # ✅ Added import

@shared_task
def generate_crm_report():
    """
    Generates a weekly CRM report via GraphQL and logs the results.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "/tmp/crm_report_log.txt"
    graphql_url = "http://localhost:8000/graphql"

    try:
        # GraphQL query
        query = """
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
        """

        # Execute GraphQL request
        response = requests.post(graphql_url, json={"query": query})
        response.raise_for_status()
        data = response.json().get("data", {})

        # Extract values
        customers = data.get("allCustomers", {}).get("totalCount", 0)
        orders_data = data.get("allOrders", {})
        orders = orders_data.get("totalCount", 0)

        # Compute total revenue
        total_revenue = 0
        for edge in orders_data.get("edges", []):
            node = edge.get("node", {})
            total_revenue += float(node.get("totalAmount", 0))

        # Log results
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - Report: {customers} customers, {orders} orders, {total_revenue:.2f} revenue\n")

    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"{timestamp} - Error generating CRM report: {e}\n")
