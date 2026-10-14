from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Feedback(models.Model):
    RECOMMEND_CHOICES = [("yes", "Yes"), ("maybe", "Maybe"), ("no", "No")]

    customer_name = models.CharField(max_length=120)
    company = models.CharField(max_length=120, blank=True)
    email = models.EmailField(blank=True)
    quality_rating = models.PositiveSmallIntegerField(
    validators=[MinValueValidator(1), MaxValueValidator(5)],
    null=True,
    blank=True,
    )

    timeliness_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
    )

    communication_rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
    )

    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    recommend = models.CharField(max_length=5, choices=RECOMMEND_CHOICES, default="yes")
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "feedback"

    def __str__(self):
        return f"{self.customer_name} ({self.rating}/5)"
