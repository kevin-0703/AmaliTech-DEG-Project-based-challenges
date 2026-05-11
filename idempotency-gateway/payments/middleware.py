from datetime import timedelta
from django.http import JsonResponse
from django.utils import timezone

from .models import ApiRateLimit


class RateLimitMiddleware:
    LIMIT = 10
    WINDOW_SECONDS = 60

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith("/api/"):

            identifier = self.get_client_ip(request)
            endpoint = request.path

            now = timezone.now()
            window_start = now - timedelta(seconds=self.WINDOW_SECONDS)

            record = ApiRateLimit.objects.filter(
                identifier=identifier,
                endpoint=endpoint
            ).first()

            if not record:
                ApiRateLimit.objects.create(
                    identifier=identifier,
                    endpoint=endpoint,
                    request_count=1,
                    window_start=now
                )
            else:
                if record.window_start < window_start:
                    record.request_count = 1
                    record.window_start = now
                    record.save()
                else:
                    if record.request_count >= self.LIMIT:
                        return JsonResponse(
                            {"error": "Rate limit exceeded."},
                            status=429
                        )

                    record.request_count += 1
                    record.save()

        return self.get_response(request)

    def get_client_ip(self, request):
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if forwarded:
            return forwarded.split(",")[0].strip()

        return request.META.get("REMOTE_ADDR", "unknown")