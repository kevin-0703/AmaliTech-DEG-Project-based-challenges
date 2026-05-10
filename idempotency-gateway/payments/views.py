from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PaymentRequestSerializer
from .services import process_payment

# Create your views here.
class ProcessPaymentView(APIView):

    def post(self, request):
        idempotency_key = request.headers.get("Idempotency-Key")

        if not idempotency_key:
            return Response(
                {"error": "Idempotency-Key header is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = PaymentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = process_payment(
            idempotency_key=idempotency_key,
            payload=serializer.validated_data
        )

        response = Response(
            result["data"],
            status=result["status"]
        )

        if result["cache_hit"]:
            response["X-Cache-Hit"] = "true"

        return response