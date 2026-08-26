from django import forms
from .models import Lent, Review

class LentForm(forms.ModelForm):
    class Meta:
        model = Lent
        fields = ['date_in', 'date_out']
        widgets = {
            'date_in': forms.DateInput(attrs={'type': 'date'}),
            'date_out': forms.DateInput(attrs={'type': 'date'}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={
                'class': 'block w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-3 border',
                'placeholder': 'Note de 0 à 10'
            }),
            'comment': forms.Textarea(attrs={
                'rows': 3,
                'class': 'block w-full border-gray-300 rounded-lg shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm p-3 border',
                'placeholder': "Partagez votre retour d'expérience..."
            }),
        }
        labels = {
            'rating': 'Note sur 10',
            'comment': 'Commentaire',
        }
        help_texts = {
            'rating': 'Donnez une note comprise entre 0 et 10.',
            'comment': 'Facultatif.',
        }
