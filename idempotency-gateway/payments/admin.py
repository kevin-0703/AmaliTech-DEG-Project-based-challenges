from django.contrib import admin
from .models import (
    Payment,
    IdempotencyRecord,
    PaymentLog,
    ApiRateLimit
)

# Register your models here.

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_ref",
        "amount",
        "currency",
        "status",
        "processed_at",
    )
    search_fields = ("transaction_ref",)
    list_filter = ("status", "currency")


@admin.register(IdempotencyRecord)
class IdempotencyRecordAdmin(admin.ModelAdmin):
    list_display = (
        "idempotency_key",
        "state",
        "status_code",
        "created_at",
        "expires_at",
    )
    search_fields = ("idempotency_key",)
    list_filter = ("state",)


@admin.register(PaymentLog)
class PaymentLogAdmin(admin.ModelAdmin):
    list_display = (
        "payment",
        "event_type",
        "created_at",
    )
    search_fields = ("event_type",)


@admin.register(ApiRateLimit)
class ApiRateLimitAdmin(admin.ModelAdmin):
    list_display = (
        "identifier",
        "endpoint",
        "request_count",
        "window_start",
    )
    search_fields = ("identifier",)