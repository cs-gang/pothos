from pothos.src.app.forms import SignupForm
from django import forms
from django.shortcuts import redirect, render
from django import http
from . import auth, forms

# Create your views here.


def index(request: http.HttpRequest) -> http.HttpResponse:
    pass


@require_POST()
def login(request: http.HttpRequest) -> http.HttpResponse:
    form = LoginForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data("email")
        password = form.cleaned_data("password")
        auth.login(request, email, password)
        return redirect("/dashboard/")
    else:
        return render(request, "login.html", {"form": form})


@require_POST()
def signup(request: http.HttpRequest) -> http.HttpResponse:
    form = SignupForm(request.POST)
    if form.is_valid():
        username = form.cleaned_data("username")
        email = form.cleaned_data("email")
        password = form.cleaned_data("password")
        user = auth.User.create(username, email, password)
        auth.login(request, email, password)
        return redirect("/dashboard/")
    else:
        return render(request, "login.html", {"form": form})
