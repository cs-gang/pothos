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
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        auth.login(request, email, password)
        return redirect("dashboard")
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
    if form.is_valid():
        username = form.cleaned_data["username"]
        email = form.cleaned_data["email"]
        password = form.cleaned_data["password"]
        currency = form.cleaned_data["currency"]

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
@auth.authenticated()
def dashboard(request: http.HttpRequest, user: auth.User) -> http.HttpResponse:
    """
    Route to render the dashboard for a user.
    """
    incomes = user.get_income_transactions()
    expenditures = user.get_expenditure_transactions()

    this_month_income = user.get_total_income()
    this_month_expenditure = user.get_total_expenditure()

    if this_month_expenditure is None and this_month_income is None:
        # both Nones, no preexisting transactions
        difference = None
    elif this_month_income is None:
        # if income none but expenditure not none, difference is negative
        difference = -this_month_expenditure
    elif this_month_expenditure is None:
        # expenditure none, so difference is positive
        difference = this_month_income
    else:
        difference = this_month_income - this_month_expenditure

    return render(
        request,
        "budget.html",
        {
            "incomes": incomes,
            "expenditures": expenditures,
            "currency": user.currency,
            "username": user.username,
            "total_income": this_month_income,
            "total_expenditure": this_month_expenditure,
            "difference": difference,
        },
    )


@require_POST
@auth.authenticated()
def create_transaction(request: http.HttpRequest, user: auth.User) -> http.HttpResponse:
    """
    Creates a new transaction for the user.
    """
    form = forms.TransactionForm(request.POST)

    if form.is_valid():
        user.create_transaction(
            transaction_type=form.cleaned_data["type"],
            amount=form.cleaned_data["amount"],
            name=form.cleaned_data["title"],
            transaction_date=form.cleaned_data["date"],
            spending_type=form.cleaned_data["spending_type"],
        )
        return redirect("dashboard")
    else:
        return http.HttpResponseServerError(
            "Something went wrong, form did not validate"
        )


@auth.authenticated()
def delete_transaction(request: http.HttpRequest, user: auth.User) -> http.HttpResponse:
    """
    Deletes a transaction with the given transaction ID.
    """
    id = int(request.POST["id"])
    user.delete_transaction(id)
    return redirect("dashboard")


@require_GET
@auth.authenticated()
def logout(request: http.HttpRequest, user: auth.User) -> http.HttpResponse:
    """
    Route to log a user out and redirect them to the main page.
    """
    auth.logout(request)
    return redirect("index")
