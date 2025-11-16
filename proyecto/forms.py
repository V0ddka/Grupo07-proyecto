# [tu_app]/forms.py
from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UsernameChangeForm(forms.Form):
    # Campo para el nuevo nombre de usuario
    nuevo_username = forms.CharField(
        label='Nuevo Nombre de Usuario', 
        max_length=150, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    def clean_nuevo_username(self):
        # Valida que el nuevo nombre de usuario no esté ya en uso
        nuevo_username = self.cleaned_data['nuevo_username']
        if User.objects.filter(username=nuevo_username).exists():
            raise ValidationError("Este nombre de usuario ya está en uso. Por favor, elige otro.")
        return nuevo_username