from django import forms

from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['email', 'name', 'patronymic', 'surname', 'comments']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control'}),
            'surname': forms.TextInput(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }