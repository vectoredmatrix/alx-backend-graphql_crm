#!/bin/bash
# clean_inactive_customers.sh
# Deletes customers with no orders since a year ago and logs the result

# Activate virtual environment if needed (uncomment if applicable)
# source /path/to/venv/bin/activate

# Navigate to Django project root (adjust path if needed)
cd "$(dirname "$0")/../.." || exit

# Execute Django shell command
deleted_count=$(python3 manage.py shell -c "
from crm.models import Customer
from django.utils import timezone
from datetime import timedelta

cutoff_date = timezone.now() - timedelta(days=365)
to_delete = Customer.objects.exclude(order__order_date__gte=cutoff_date).distinct()
count = to_delete.count()
to_delete.delete()
print(count)
")

# Log output with timestamp
timestamp=$(date '+%Y-%m-%d %H:%M:%S')
echo \"[\$timestamp] Deleted \$deleted_count inactive customers.\" >> /tmp/customer_cleanup_log.txt
