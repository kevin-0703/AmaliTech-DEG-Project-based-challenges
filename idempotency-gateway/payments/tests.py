from django.test import TestCase
from rest_framework.test import APIClient

# Create your tests here.

class PaymentApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/process-payment"

    def test_missing_idempotency_header(self):
        response = self.client.post(
            self.url,
            {"amount": 100, "currency": "RWF"},
            format="json"
        )

        self.assertEqual(response.status_code, 400)

    def test_first_payment_success(self):
        response = self.client.post(
            self.url,
            {"amount": 100, "currency": "RWF"},
            format="json",
            HTTP_IDEMPOTENCY_KEY="abc123"
        )

        self.assertEqual(response.status_code, 201)
        self.assertIn("transaction_ref", response.data)

    def test_duplicate_returns_cached_response(self):
        self.client.post(
            self.url,
            {"amount": 100, "currency": "RWF"},
            format="json",
            HTTP_IDEMPOTENCY_KEY="dup001"
        )

        response = self.client.post(
            self.url,
            {"amount": 100, "currency": "RWF"},
            format="json",
            HTTP_IDEMPOTENCY_KEY="dup001"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response["X-Cache-Hit"], "true")

    def test_same_key_different_payload_rejected(self):
        self.client.post(
            self.url,
            {"amount": 100, "currency": "RWF"},
            format="json",
            HTTP_IDEMPOTENCY_KEY="fraud001"
        )

        response = self.client.post(
            self.url,
            {"amount": 500, "currency": "RWF"},
            format="json",
            HTTP_IDEMPOTENCY_KEY="fraud001"
        )

        self.assertEqual(response.status_code, 422)

    def test_invalid_amount_rejected(self):
        response = self.client.post(
            self.url,
            {"amount": -5, "currency": "RWF"},
            format="json",
            HTTP_IDEMPOTENCY_KEY="bad001"
        )

        self.assertEqual(response.status_code, 400)

    def test_rate_limit_triggered(self):
        for i in range(10):
            self.client.post(
                self.url,
                {"amount": 100, "currency": "RWF"},
                format="json",
                HTTP_IDEMPOTENCY_KEY=f"rate{i}"
            )

        response = self.client.post(
            self.url,
            {"amount": 100, "currency": "RWF"},
            format="json",
            HTTP_IDEMPOTENCY_KEY="rate-final"
        )

        self.assertEqual(response.status_code, 429)

    def test_duplicate_response_same_transaction_ref(self):
        first = self.client.post(
            self.url,
            {"amount": 100, "currency": "RWF"},
            format="json",
            HTTP_IDEMPOTENCY_KEY="same001"
        )

        second = self.client.post(
            self.url,
            {"amount": 100, "currency": "RWF"},
            format="json",
            HTTP_IDEMPOTENCY_KEY="same001"
        )

        self.assertEqual(
            first.data["transaction_ref"],
            second.data["transaction_ref"]
        )  
         