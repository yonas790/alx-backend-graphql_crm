#!/bin/bash

# Get the current timestamp
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Run Django manage.py shell to delete customers with no orders in the last year
DELETED_COUNT=$(python manage.py shell -c "
from django.utils import timezone
from datetime import timedelta
from crm.models import Customer
from django.db.models import Max

# Calculate the date one year ago
one_year_ago = timezone.now() - timedelta(days=365)

# Find customers with no orders or whose latest order is older than one year
customers = Customer.objects.annotate(last_order=Max('order__created_at')).filter(
    last_order__isnull=True
) | Customer.objects.annotate(last_order=Max('order__created_at')).filter(
    last_order__lt=one_year_ago
)

# Count and delete customers
count = customers.count()
customers.delete()
print(count)
" 2>/dev/null)

# Log the result with timestamp to /tmp/customer_cleanup_log.txt
echo "[$TIMESTAMP] Deleted $DELETED_COUNT inactive customers" >> /tmp/customer_cleanup_log.txt