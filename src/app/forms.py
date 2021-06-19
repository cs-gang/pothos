from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=50)
    password = forms.CharField(max_length=20)


class SignupForm(forms.Form):
    username = forms.CharField(max_length=10)
    email = forms.EmailField(max_length=50)
    password = forms.CharField(max_length=20)
    currency = forms.CharField(max_length=3)
