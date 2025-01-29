# Copyright (c) 2025 AYEBATARIWALATE YEKOROGHA. All rights reserved.
from allauth.account.forms import LoginForm as AllauthLoginForm
from allauth.account.forms import SignupForm as AllauthSignupForm
from django import forms


class LogInForm(AllauthLoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Customize the 'login' field (username or email) widget
        self.fields['login'].widget = forms.TextInput(attrs={
            'placeholder': 'Your Username or Email',
            'class': 'block w-full mt-1 p-2 border rounded-lg'
        })
        # Customize the 'password' field widget
        self.fields['password'].widget = forms.PasswordInput(attrs={
            'placeholder': 'Your Password',
            'class': 'block w-full mt-1 p-2 border rounded-lg'
        })
        # Customize the 'remember' field widget (if applicable)
        if 'remember' in self.fields:
            self.fields['remember'].widget = forms.CheckboxInput(attrs={
                'class': 'form-checkbox h-4 w-4 text-blue-600'
            })


class SignUpForm(AllauthSignupForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Apply design to fields
        self.fields['username'].widget = forms.TextInput(attrs={
            'placeholder': 'Your Username',
            'class': 'block w-full mt-1 p-2 border rounded-lg'
        })
        self.fields['email'].widget = forms.EmailInput(attrs={
            'placeholder': 'Your Email Address',
            'class': 'block w-full mt-1 p-2 border rounded-lg'
        })
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'placeholder': 'Your Password',
            'class': 'block w-full mt-1 p-2 border rounded-lg'
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'placeholder': 'Repeat Password',
            'class': 'block w-full mt-1 p-2 border rounded-lg'
        })

    def save(self, request):
        return super().save(request)