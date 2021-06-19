from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(max_length=50)
    password = forms.CharField(max_length=20)


class SignupForm(forms.Form):
    username = forms.CharField(max_length=10)
    email = forms.EmailField(max_length=50)
    password = forms.CharField(max_length=20)
    currency = forms.CharField(max_length=3)


class NewTransactionForm(forms.Form):
    title = forms.CharField(max_length=35)
    amount = forms.FloatField()
    type = forms.CharField(max_length=11)
    date = forms.DateField()
    spending_type = forms.CharField(max_length=14, required=False)
    notes = forms.CharField(max_length=300, required=False)
