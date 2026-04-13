from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Campaign, Client, Note, Task


class AgencyAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (css + " form-control").strip()


class AdminUserCreateForm(UserCreationForm):
    is_staff = forms.BooleanField(required=False, label="Admin access")

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "is_staff")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            css = field.widget.attrs.get("class", "")
            if name == "is_staff":
                field.widget.attrs["class"] = (css + " form-check-input").strip()
            else:
                field.widget.attrs["class"] = (css + " form-control").strip()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = self.cleaned_data.get("is_staff", False)
        if commit:
            user.save()
        return user


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ("name",)
        widgets = {"name": forms.TextInput(attrs={"class": "form-control"})}


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = ("name", "clicks", "spend", "conversions")
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "clicks": forms.NumberInput(attrs={"class": "form-control"}),
            "spend": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "conversions": forms.NumberInput(attrs={"class": "form-control"}),
        }


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ("content",)
        widgets = {
            "content": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ("description", "due_date")
        widgets = {
            "due_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "description": forms.TextInput(attrs={"class": "form-control"}),
        }
