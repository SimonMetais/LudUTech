from django import forms
from .models import Lent

class LentForm(forms.ModelForm):
    class Meta:
        model = Lent
        fields = ['date_in', 'date_out']
        widgets = {
            'date_in': forms.DateInput(attrs={'type': 'date'}),
            'date_out': forms.DateInput(attrs={'type': 'date'}),
        }
