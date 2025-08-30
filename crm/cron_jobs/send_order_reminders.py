from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from datetime import datetime, timedelta
import pytz

# Set up GraphQL client
transport = AIOHTTPTransport(url="http://localhost:8000/graphql")
client = Client(transport=transport, fetch_schema_from_transport=True)

# Define GraphQL query for orders within the last 7 days
query = gql("""
    query {
        orders(orderDate_Gte: "%s") {
            edges {
                node {
                    id
                    customer {
                        email
                    }
                }
            }
        }
    }
""")

# Calculate the date 7 days ago in ISO format
eat_tz = pytz.timezone("Africa/Nairobi")
now = datetime.now(eat_tz)
seven_days_ago = (now - timedelta(days=7)).isoformat()

# Execute the query
result = client.execute(query, variable_values={"orderDate_Gte": seven_days_ago})

# Get current timestamp for logging
timestamp = now.strftime("%Y-%m-%d %H:%M:%S")

# Log order details to file
with open("/tmp/order_reminders_log.txt", "a") as log_file:
    for edge in result["orders"]["edges"]:
        order_id = edge["node"]["id"]
        customer_email = edge["node"]["customer"]["email"]
        log_file.write(f"[{timestamp}] Order ID: {order_id}, Customer Email: {customer_email}\n")

# Print confirmation to console
print("Order reminders processed!")