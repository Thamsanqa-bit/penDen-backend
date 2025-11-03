# apps/orders/tasks.py
from celery import shared_task
from tenacity import retry, wait_exponential, stop_after_attempt
import requests
import pybreaker

# Circuit breaker for payment API
payment_breaker = pybreaker.CircuitBreaker(fail_max=3, reset_timeout=60)

@shared_task(bind=True, max_retries=5)
@retry(wait=wait_exponential(multiplier=1, min=2, max=10), stop=stop_after_attempt(3))
@payment_breaker
def process_payment(self, order_id, payload):
    try:
        response = requests.post("https://api.payfast.co.za/pay", json=payload, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)
