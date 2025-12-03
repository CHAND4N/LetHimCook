from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone_number = forms.CharField(max_length=15, required=True)
    role = forms.ChoiceField(
        choices=Profile.ROLE_CHOICES,
        required=True,
        initial='user'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'phone_number', 'role')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile = user.profile
            profile.phone_number = self.cleaned_data['phone_number']
            profile.role = self.cleaned_data['role']
            profile.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)
    password = forms.CharField(widget=forms.PasswordInput, required=True)

