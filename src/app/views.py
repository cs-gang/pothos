from django import http
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_POST

from . import auth, forms


def index(request: http.HttpRequest) -> http.HttpResponse:
    return render(request, "index.html")


@require_POST
def login(request: http.HttpRequest) -> http.HttpResponse:
    """
    Route to validate user logins.
    """
    form = forms.LoginForm(request.POST)
    if form.is_valid():
        email = form.cleaned_data("email")
        password = form.cleaned_data("password")
        auth.login(request, email, password)
        return redirect("/dashboard/")
    else:
        return http.HttpResponseServerError(
            "Something went wrong, form did not validate."
        )


@require_POST
def signup(request: http.HttpRequest) -> http.HttpResponse:
    """
    Route to sign a new user up to Pothos.
    """
    form = forms.SignupForm(request.POST)
    print(request.POST)
    if form.is_valid():
        username = form.cleaned_data("username")
        email = form.cleaned_data("email")
        password = form.cleaned_data("password")
        currency = form.cleaned_data("currency")

        user = auth.User.create(
            username=username, email=email, password=password, currency=currency
        )
        auth.login(request, email, password)
        return redirect("dashboard")
    else:
        return http.HttpResponseServerError(
            "Something went wrong; the form did not validate."
        )


@require_GET
def dashboard(request: http.HttpRequest) -> http.HttpResponse:
    """
    Route to render the dashboard for a user.
    """
    return http.HttpResponse("hi sign in worked bro")
