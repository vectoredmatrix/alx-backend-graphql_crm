# CRM Celery Setup

## Installation

1. **Install Redis and dependencies**
   ```bash
   sudo apt install redis-server
   pip install -r requirements.txt
   ```

python manage.py migrate
celery -A crm worker -l info
celery -A crm beat -l info
