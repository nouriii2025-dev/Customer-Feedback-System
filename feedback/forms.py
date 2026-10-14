from django import forms

from .models import Feedback


class FeedbackForm(forms.ModelForm):
    rating = forms.TypedChoiceField(
        choices=[(i, str(i)) for i in range(1, 6)],
        coerce=int,
        widget=forms.RadioSelect,
        label="How would you rate your overall experience?",
    )
    recommend = forms.ChoiceField(
        choices=Feedback.RECOMMEND_CHOICES,
        widget=forms.RadioSelect,
        label="Would you recommend us to others?",
    )

    class Meta:
        model = Feedback
        fields = ["customer_name", "company", "email", "rating", "recommend", "comments"]
        labels = {
            "customer_name": "Your name",
            "company": "Company",
            "email": "Email",
            "comments": "Anything else you'd like to tell us?",
        }
        widgets = {"comments": forms.Textarea(attrs={"rows": 4})}
