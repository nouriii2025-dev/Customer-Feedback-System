import json
from smtplib import SMTPAuthenticationError
from unittest.mock import patch

from django.test import TestCase, override_settings


class DashboardAccessTests(TestCase):
    def test_dashboard_is_available_without_login(self):
        response = self.client.get("/dashboard/")

        self.assertEqual(response.status_code, 200)

    @patch("feedback.views.sync_workbook", return_value=(None, 0))
    def test_export_update_is_available_without_login(self, sync_workbook):
        response = self.client.post("/dashboard/export/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ok"], True)
        sync_workbook.assert_called_once()


@override_settings(
    FEEDBACK_SMTP_HOST="smtp.example.com",
    FEEDBACK_SMTP_USERNAME="",
    FEEDBACK_SMTP_PASSWORD="",
    FEEDBACK_SMTP_USE_TLS=True,
    FEEDBACK_SMTP_USE_SSL=False,
    DEFAULT_FROM_EMAIL="feedback@example.com",
)
class SendEmailTests(TestCase):
    def post_email(self, to="customer@example.com", subject="Feedback", message="Please share feedback."):
        return self.client.post(
            "/dashboard/email/",
            data=json.dumps({"to": to, "subject": subject, "message": message}),
            content_type="application/json",
        )

    def test_email_fields_are_sent_to_recipient(self):
        with patch("feedback.views.send_mail", return_value=1) as send_mail:
            response = self.post_email()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True, "sent": 1})
        send_mail.assert_called_once_with(
            "Feedback",
            "Please share feedback.",
            "feedback@example.com",
            ["customer@example.com"],
            fail_silently=False,
        )

    def test_success_requires_server_acceptance(self):
        with patch("feedback.views.send_mail", return_value=0):
            response = self.post_email()

        self.assertEqual(response.status_code, 502)
        self.assertFalse(response.json()["ok"])
        self.assertIn("did not accept", response.json()["error"])

    def test_smtp_failure_is_reported(self):
        failure = SMTPAuthenticationError(535, b"Authentication failed")
        with patch("feedback.views.send_mail", side_effect=failure):
            response = self.post_email()

        self.assertEqual(response.status_code, 502)
        self.assertFalse(response.json()["ok"])
        self.assertIn("Authentication failed", response.json()["error"])


class EmailConfigurationTests(TestCase):
    @override_settings(
        FEEDBACK_SMTP_HOST="",
        DEFAULT_FROM_EMAIL="feedback@example.com",
    )
    def test_unconfigured_smtp_does_not_report_success(self):
        response = self.client.post(
            "/dashboard/email/",
            data=json.dumps({
                "to": "customer@example.com",
                "subject": "Feedback",
                "message": "Please share feedback.",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 503)
        self.assertIn("set EMAIL_HOST", response.json()["error"])

    @override_settings(
        FEEDBACK_SMTP_HOST="smtp.gmail.com",
        FEEDBACK_SMTP_USERNAME="",
        FEEDBACK_SMTP_PASSWORD="",
    )
    def test_gmail_requires_environment_credentials(self):
        response = self.client.post(
            "/dashboard/email/",
            data=json.dumps({
                "to": "customer@example.com",
                "subject": "Feedback",
                "message": "Please share feedback.",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 503)
        self.assertIn("Google App Password", response.json()["error"])
