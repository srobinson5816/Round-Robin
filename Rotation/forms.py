from django import forms
from .models import Tech, Settings
import os

class TechForm(forms.ModelForm):
    class Meta:
        model = Tech
        fields = ['name', 'active']

class SettingsForm(forms.Form):
    database_location = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Enter the relative path to the database file from the project root."
    )
