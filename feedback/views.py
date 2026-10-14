import json
from smtplib import SMTPException

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.mail import BadHeaderError, send_mail
from django.core.paginator import Paginator
from django.core.validators import validate_email
from django.db.models import Avg, Count, Max, Q
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .excel import WorkbookLocked, analysis_path, sync_workbook
from .forms import FeedbackForm
from .models import Feedback


def _form_link(request):
    return getattr(settings, "FEEDBACK_FORM_URL", "") or request.build_absolute_uri(
        reverse("feedback:form")
    )


def _email_template(link):
    company = settings.FEEDBACK_COMPANY_NAME
    subject = f"How did we do? Share your feedback with {company}"
    body = (
        "Hello,\n\n"
        f"Thank you for choosing {company}. We'd really value a minute of your time "
        "to hear about your experience with our products and service.\n\n"
        f"You can share your feedback here (no login needed):\n{link}\n\n"
        "Your comments help us improve, and we read every response.\n\n"
        f"Best regards,\n{company}"
    )
    return subject, body


@require_GET
def dashboard(request):
    everything = Feedback.objects.all()
    agg = everything.aggregate(total=Count("id"), avg=Avg("rating"), last=Max("created_at"))
    total = agg["total"]
    recommend_pct = (
        round(everything.filter(recommend="yes").count() / total * 100) if total else None
    )

    qs = everything
    q = request.GET.get("q", "").strip()
    if q:
        qs = qs.filter(
            Q(customer_name__icontains=q) | Q(company__icontains=q)
            | Q(email__icontains=q) | Q(comments__icontains=q)
        )
    rating = request.GET.get("rating", "")
    if rating.isdigit() and 1 <= int(rating) <= 5:
        qs = qs.filter(rating=int(rating))

    page = Paginator(qs, 15).get_page(request.GET.get("page"))
    params = request.GET.copy()
    params.pop("page", None)

    link = _form_link(request)
    subject, body = _email_template(link)
    path = analysis_path()
    last_export = (
        timezone.make_aware(timezone.datetime.fromtimestamp(path.stat().st_mtime))
        if path.exists() else None
    )
    return render(request, "feedback/dashboard.html", {
        "page": page, "q": q, "rating": rating, "filtered": bool(q or rating),
        "total": total, "avg": agg["avg"], "last": agg["last"],
        "recommend_pct": recommend_pct, "pips": range(1, 6),
        "form_link": link, "email_subject": subject, "email_body": body,
        "last_export": last_export, "qs": params.urlencode(),
    })


def feedback_form(request):
    form = FeedbackForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("feedback:thanks")
    return render(request, "feedback/form.html", {"form": form})


def thanks(request):
    return render(request, "feedback/thanks.html")


@require_POST
def export_update(request):
    try:
        _, count = sync_workbook(Feedback.objects.all())
    except WorkbookLocked:
        return JsonResponse(
            {"ok": False, "error": "The analysis sheet is open in Excel. Close it and try again."},
            status=409,
        )
    return JsonResponse({"ok": True, "count": count,
                         "download": reverse("feedback:export_download")})


@require_GET
def export_download(request):
    path = analysis_path()
    if not path.exists():
        raise Http404("Nothing exported yet.")
    return FileResponse(open(path, "rb"), as_attachment=True, filename=path.name)


@require_POST
def send_email(request):
    try:
        data = json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid request."}, status=400)

    recipients = [r.strip() for r in str(data.get("to", "")).replace(";", ",").split(",") if r.strip()]
    subject = str(data.get("subject", "")).strip()
    message = str(data.get("message", "")).strip()
    if not recipients:
        return JsonResponse({"ok": False, "error": "Enter a recipient email address."}, status=400)
    for r in recipients:
        try:
            validate_email(r)
        except ValidationError:
            return JsonResponse({"ok": False, "error": f"“{r}” is not a valid email address."}, status=400)
    if not subject or not message:
        return JsonResponse({"ok": False, "error": "Subject and message can't be empty."}, status=400)

    if not settings.FEEDBACK_SMTP_HOST:
        return JsonResponse(
            {"ok": False, "error": "Email sending is not configured: set EMAIL_HOST."},
            status=503,
        )
    if settings.FEEDBACK_SMTP_HOST.lower() == "smtp.gmail.com" and not (
        settings.FEEDBACK_SMTP_USERNAME and settings.FEEDBACK_SMTP_PASSWORD
    ):
        return JsonResponse(
            {
                "ok": False,
                "error": (
                    "Gmail SMTP requires EMAIL_HOST_USER (your Gmail address) and "
                    "EMAIL_HOST_PASSWORD (a Google App Password) in the environment."
                ),
            },
            status=503,
        )
    if not settings.DEFAULT_FROM_EMAIL:
        return JsonResponse(
            {"ok": False, "error": "Email sending is not configured: set DEFAULT_FROM_EMAIL."},
            status=503,
        )
    if bool(settings.FEEDBACK_SMTP_USERNAME) != bool(settings.FEEDBACK_SMTP_PASSWORD):
        return JsonResponse(
            {"ok": False, "error": "Set both EMAIL_HOST_USER and EMAIL_HOST_PASSWORD, or leave both empty."},
            status=503,
        )
    if settings.FEEDBACK_SMTP_USE_TLS and settings.FEEDBACK_SMTP_USE_SSL:
        return JsonResponse(
            {"ok": False, "error": "Email configuration can't enable both TLS and SSL."},
            status=503,
        )

    try:
        for recipient in recipients:
            sent_count = send_mail(
                subject, message, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=False
            )
            if sent_count != 1:
                return JsonResponse(
                    {"ok": False, "error": f"The email server did not accept the message for {recipient}."},
                    status=502,
                )
    except (BadHeaderError, ImproperlyConfigured, OSError, SMTPException, ValueError) as exc:
        detail = str(exc).strip() or exc.__class__.__name__
        return JsonResponse(
            {"ok": False, "error": f"Email delivery failed: {detail}"},
            status=502,
        )
    return JsonResponse({"ok": True, "sent": len(recipients)})
