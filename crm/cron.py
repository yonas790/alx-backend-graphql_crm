from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport
from datetime import datetime
import pytz

def log_crm_heartbeat():
    # Set up GraphQL client
    transport = AIOHTTPTransport(url="http://localhost:8000/graphql")
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