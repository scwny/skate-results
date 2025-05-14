from django import forms
from core.models import Skater, Club, ScheduledSkater, Event

class ResultImageUploadForm(forms.Form):
    image = forms.ImageField(required=False)
    image_url = forms.URLField(required=False)
    status = forms.ChoiceField(
        choices=Event.STATUS_CHOICES,
        required=False,
        label="Event Status"
    )

    def clean(self):
        cleaned = super().clean()
        image = cleaned.get("image")
        url = cleaned.get("image_url")
        if not image and not url and not cleaned.get("status"):
            raise forms.ValidationError("Please upload an image, provide a URL, or choose a status.")
        return cleaned


class SkaterEditForm(forms.ModelForm):
    class Meta:
        model = Skater
        fields = ["firstName", "lastName", "club"]

class ScheduledSkaterEditForm(forms.ModelForm):
    class Meta:
        model = ScheduledSkater
        fields = ["scratch"]

class ResultUploadForm(forms.Form):
    image = forms.ImageField(label="Upload Result Sheet")