import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from feedback.models import Feedback

SAMPLES = [
    ("Rashid Al Mansoori", "Gulf Power Services", 5, "yes", "Calibration certificates arrived a day early and the documentation was spotless."),
    ("Priya Nair", "Emirates Water Works", 4, "yes", "Good technical support. Would like faster updates on order status."),
    ("Omar Haddad", "Petrofield LLC", 5, "yes", "WIKA gauges were exactly as specified. Smooth process end to end."),
    ("Sara Whitfield", "Desert Utilities", 3, "maybe", "Quality is fine but quotation turnaround was slower than expected."),
    ("Imran Qureshi", "Al Noor Refinery", 4, "yes", "Reliable team. On-site calibration was well organised."),
    ("Layla Farouk", "Gulf Power Services", 5, "yes", ""),
    ("Daniel Mercer", "Horizon Energy", 2, "no", "Delivery was delayed twice and we had to chase for updates."),
    ("Fatima Al Zaabi", "Emirates Water Works", 4, "yes", "Professional and responsive. Pricing is competitive."),
    ("Vikram Shah", "Petrofield LLC", 5, "yes", "Excellent service on the Trafag transmitters."),
    ("Noura Saeed", "Desert Utilities", 3, "maybe", "Average experience. Communication could be clearer."),
]


class Command(BaseCommand):
    help = "Create sample feedback so the dashboard has something to show."

    def handle(self, *args, **opts):
        now = timezone.now()
        for i, (name, company, rating, rec, text) in enumerate(SAMPLES):
            slug = name.lower().replace(" ", ".")
            fb = Feedback.objects.create(
                customer_name=name, company=company, rating=rating, recommend=rec,
                comments=text, email=f"{slug}@example.com",
            )
            Feedback.objects.filter(pk=fb.pk).update(
                created_at=now - timedelta(days=random.randint(0, 30), hours=i)
            )
        self.stdout.write(self.style.SUCCESS(f"Created {len(SAMPLES)} sample responses"))
