#!/usr/bin/env python3
"""
send_order_reminders.py
Uses gql to query recent orders and logs reminders.
"""

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime, timedelta

# GraphQL endpoint
GRAPHQL_URL = "http://localhost:8000/graphql"

# Log file
LOG_FILE = "/tmp/order_reminders_log.txt"

# Create GraphQL client
transport = RequestsHTTPTransport(url=GRAPHQL_URL, verify=True, retries=3)
client = Client(transport=transport, fetch_schema_from_transport=False)

# Compute last 7 days
week_ago = datetime.utcnow() - timedelta(days=7)

# GraphQL query
query = gql("""
query RecentOrders($startDate: DateTime!) {
  allOrders(order_Date_Gte: $startDate, orderBy: "-order_date") {
    edges {
      node {
        id
        orderDate
        customer {
          email
        }
      }
    }
  }
}
""")

variables = {"startDate": week_ago.isoformat()}
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

try:
    result = client.execute(query, variable_values=variables)
    orders = result.get("allOrders", {}).get("edges", [])

    with open(LOG_FILE, "a") as f:
        for order in orders:
            node = order.get("node", {})
            order_id = node.get("id")
            email = node.get("customer", {}).get("email")
            f.write(f"[{timestamp}] Reminder for Order ID: {order_id}, Customer: {email}\n")

    print("Order reminders processed!")

except Exception as e:
    with open(LOG_FILE, "a") as f:
        f.write(f"[{timestamp}] Error: {e}\n")
    print("Error occurred while processing order reminders!")
