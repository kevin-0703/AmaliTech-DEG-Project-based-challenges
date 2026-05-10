from django.db import models
import uuid
from django.core.serializers.json import DjangoJSONEncoder

# Create your models here.
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class IdempotencyRecord(BaseModel):
    STATE_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    idempotency_key = models.CharField(max_length=255, unique=True)
    request_hash = models.CharField(max_length=64)
    request_body = models.JSONField(encoder=DjangoJSONEncoder)
    response_body = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)
    status_code = models.IntegerField(null=True, blank=True)
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default="pending")
    expires_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["idempotency_key"]),
            models.Index(fields=["state"]),
        ]

    def __str__(self):
        return self.idempotency_key


class Payment(BaseModel):
    STATUS_CHOICES = [
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=10)
    transaction_ref = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="success")
    processed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_ref


class PaymentLog(BaseModel):
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE,
        related_name="logs"
    )
    event_type = models.CharField(max_length=50)
    message = models.TextField()
    ip_address = models.CharField(max_length=45, blank=True, null=True)
    user_agent = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.event_type


class ApiRateLimit(BaseModel):
    identifier = models.CharField(max_length=255)
    endpoint = models.CharField(max_length=255)
    request_count = models.IntegerField(default=0)
    window_start = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=["identifier"]),
            models.Index(fields=["endpoint"]),
        ]

    def __str__(self):
        return self.identifier