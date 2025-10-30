#!/usr/bin/env python3
"""
send_order_reminders.py
Queries GraphQL API for orders within the last 7 days and logs reminders.
"""

import requests
import datetime
from datetime import timedelta

# GraphQL endpoint
GRAPHQL_URL = "http://localhost:8000/graphql"

# Log file path
LOG_FILE = "/tmp/order_reminders_log.txt"

# Calculate date range (last 7 days)
now = datetime.datetime.utcnow()
week_ago = now - timedelta(days=7)

# GraphQL query
query = """
query RecentOrders($startDate: DateTime!) {
  allOrders(orderBy: "-order_date", order_Date_Gte: $startDate) {
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
"""

# Prepare payload
variables = {"startDate": week_ago.isoformat()}

try:
    response = requests.post(GRAPHQL_URL, json={"query": query, "variables": variables})
    response.raise_for_status()
    data = response.json()

    # Extract orders
    orders = data.get("data", {}).get("allOrders", {}).get("edges", [])
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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