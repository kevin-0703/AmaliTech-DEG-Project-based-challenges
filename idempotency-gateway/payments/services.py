import time
import uuid
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

from .models import Payment, IdempotencyRecord
from .utils import generate_request_hash


def process_payment(idempotency_key, payload):
    request_hash = generate_request_hash(payload)

    existing = IdempotencyRecord.objects.filter(
        idempotency_key=idempotency_key
    ).first()

    # if existing key is found
    if existing:

        # if the same key is found but request body modified 
        if existing.request_hash != request_hash:
            return {
                "status": 422,
                "data": {
                    "error": "Idempotency key already used for a different request body."
                },
                "cache_hit": False
            }

        # Return cached successful response
        if existing.state == "success":
            return {
                "status": existing.status_code,
                "data": existing.response_body,
                "cache_hit": True
            }

    # First request
    record = IdempotencyRecord.objects.create(
        idempotency_key=idempotency_key,
        request_hash=request_hash,
        request_body=payload,
        state="pending",
        expires_at=timezone.now() + timedelta(hours=24)
    )

    # Simulate payment gateway delay
    time.sleep(2)

    transaction_ref = str(uuid.uuid4())

    Payment.objects.create(
        amount=Decimal(payload["amount"]),
        currency=payload["currency"],
        transaction_ref=transaction_ref,
        status="success"
    )

    response_data = {
        "message": f'Charged {payload["amount"]} {payload["currency"]}',
        "transaction_ref": transaction_ref
    }

    record.response_body = response_data
    record.status_code = 201
    record.state = "success"
    record.save()

    return {
        "status": 201,
        "data": response_data,
        "cache_hit": False
    }