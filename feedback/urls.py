from django.urls import path

from . import views

app_name = "feedback"

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/export/", views.export_update, name="export"),
    path("dashboard/export/download/", views.export_download, name="export_download"),
    path("dashboard/email/", views.send_email, name="send_email"),
    path("feedback/", views.feedback_form, name="form"),
    path("feedback/thanks/", views.thanks, name="thanks"),
]
