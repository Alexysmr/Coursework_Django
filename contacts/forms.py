from django import forms

from .models import Contact

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['username', 'phone', 'email', 'message']
        labels = {
            'username': 'Ваше имя',
            'phone': 'Телефон',
            'email': 'Email',
            'message': 'Сообщение',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control'}),
        }