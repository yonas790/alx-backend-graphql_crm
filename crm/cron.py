from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from datetime import datetime
import pytz

def log_crm_heartbeat():
    # Set up GraphQL client with RequestsHTTPTransport
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Define GraphQL query for hello field
    query = gql("""
        query {
            hello
        }
    """)

    # Execute the query (optional, to verify endpoint responsiveness)
    try:
        response = client.execute(query)
    except Exception:
        pass  # Query is optional, so silently handle failures

    # Get current timestamp in EAT timezone
    eat_tz = pytz.timezone("Africa/Nairobi")
    now = datetime.now(eat_tz)
    timestamp = now.strftime("%d/%m/%Y-%H:%M:%S")

    # Log heartbeat message to file
    with open("/tmp/crm_heartbeat_log.txt", "a") as log_file:
        log_file.write(f"{timestamp} CRM is alive\n")

def update_low_stock():
    # Set up GraphQL client with RequestsHTTPTransport
    transport = RequestsHTTPTransport(url="http://localhost:8000/graphql")
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # Define GraphQL mutation for updating low-stock products
    mutation = gql("""
        mutation {
            updateLowStockProducts {
                products {
                    name
                    stock
                }
                message
            }
        }
    """)

    # Execute the mutation
    try:
        result = client.execute(mutation)
        products = result.get("updateLowStockProducts", {}).get("products", [])
        
        # Get current timestamp in EAT timezone
        eat_tz = pytz.timezone("Africa/Nairobi")
        now = datetime.now(eat_tz)
        timestamp = now.strftime("%d/%m/%Y-%H:%M:%S")

        # Log updated products to file
        with open("/tmp/low_stock_updates_log.txt", "a") as log_file:
            for product in products:
                log_file.write(f"[{timestamp}] Updated {product['name']} to stock {product['stock']}\n")
    except Exception as e:
        # Log error if mutation fails
        with open("/tmp/low_stock_updates_log.txt", "a") as log_file:
            log_file.write(f"[{timestamp}] Error updating low-stock products: {str(e)}\n")