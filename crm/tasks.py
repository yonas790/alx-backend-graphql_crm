# crm/tasks.py
import os
from datetime import datetime
from celery import shared_task
from django.utils.timezone import now
from graphene_django.settings import graphene_settings

@shared_task
def generate_crm_report():
    # Example GraphQL query
    query = """
    {
      customersCount
      ordersCount
      totalRevenue
    }
    """

    schema = graphene_settings.SCHEMA
    result = schema.execute(query)

    if result.errors:
        report_line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - ERROR: {result.errors}\n"
    else:
        customers = result.data.get("customersCount", 0)
        orders = result.data.get("ordersCount", 0)
        revenue = result.data.get("totalRevenue", 0)

        report_line = (
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
            f"- Report: {customers} customers, {orders} orders, {revenue} revenue\n"
        )

    log_path = "/tmp/crm_report_log.txt"
    with open(log_path, "a") as f:
        f.write(report_line)

    return report_line
