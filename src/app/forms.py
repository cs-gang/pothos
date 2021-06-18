from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=20, label="")
    password = forms.CharField(max_length=20, label="")


class SignupForm(forms.Form):
    username = forms.CharField(label="", max_length=10)
    email = forms.EmailField(label="", max_length=20)
    password = forms.CharField(label="", max_length=20)
    currency = forms.CharField(label="")
