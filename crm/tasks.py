# crm/tasks.py
import requests
from datetime import datetime
from celery import shared_task

@shared_task
def generate_crm_report():
    url = "http://localhost:8000/graphql/"
    query = """
    {
      customersCount
      ordersCount
      totalRevenue
    }
    """

    try:
        response = requests.post(url, json={"query": query})
        data = response.json()

        if "errors" in data:
            report_line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR: {data['errors']}\n"
        else:
            customers = data["data"].get("customersCount", 0)
            orders = data["data"].get("ordersCount", 0)
            revenue = data["data"].get("totalRevenue", 0)

            report_line = (
                f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
                f"- Report: {customers} customers, {orders} orders, {revenue} revenue\n"
            )
    except Exception as e:
        report_line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR: {str(e)}\n"

    log_path = "/tmp/crm_report_log.txt"
    with open(log_path, "a") as f:
        f.write(report_line)

    return report_line
