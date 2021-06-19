"""Functions and classes to help authenticate users with Firebase."""
import json
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, Callable, Literal, Optional, Union
from django.db.models.query import QuerySet
from django.http.request import HttpRequest

import requests
import firebase_admin
from decouple import config
from django import http
from firebase_admin import auth, credentials, exceptions
from firebase_admin.auth import UserRecord

from . import models


API_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
API_KEY = config("FIREBASE_API_KEY")

cred = credentials.Certificate("./src/firebase-credentials.json")
app = firebase_admin.initialize_app(cred)


def _create_user(
    app: firebase_admin.App, *, username: str, email: str, password: str
) -> Optional[UserRecord]:
    """
    Creates a new user on Firebase.
    This function does not create the user in our database.
    """
    try:
        user = auth.create_user(
            app=app, display_name=username, email=email, password=password
        )
        return user
    except Exception as e:
        if isinstance(e, ValueError):
            raise ValueError("Invalid values provided") from e
        elif isinstance(e, exceptions.FirebaseError):
            raise RuntimeError(
                f"Firebase raised an error while creating user {username}"
            ) from e


def _save_user_to_db(user: UserRecord, currency: str) -> models.User:
    """
    Saves a user to our database.
    This function is meant to be used after a user is created on firebase.
    """
    _db_user = models.User(
        id=user.uid, username=user.display_name, email=user.email, currency=currency
    )
    _db_user.save()
    return _db_user


def _get_user_from_db(uid: str) -> models.User:
    """
    Retrieve a user from our database.
    """
    return models.User.objects.get(pk=uid)


def get_user(app: firebase_admin.App, uid: str) -> UserRecord:
    """
    Gets a user from firebase.
    """
    return auth.get_user(app=app, uid=uid)


def authenticate_user(email: str, password: str) -> Optional[dict]:
    """
    Authenticate a user with email and password.
    This will be used while logging in.

    Returns:
        None, if the user failed authentication
        Raw response dictionary from the API if the user passed authentication.
        This dictionary will be added to the user's `session` to retrieve user ID later.
    """
    payload = json.dumps(
        {"email": email, "password": password, "returnSecureToken": True}
    )
    response = requests.post(API_URL, params={"key": API_KEY}, data=payload)

    data = response.json()

    if not data.get("idToken"):
        # the API didn't give back a regenerate token, so the authentication was a failure
        return
    else:
        return data


def create_session_cookie(data: dict) -> Union[dict, Literal[False]]:
    """
    Creates a session cookie for a user with the given `idToken`.
    Arguments ::
        data: dict -> The raw response dictionary sent by the Firebase API on a succesful login.
        This will be returned by the `authenticate_user` function.
    Returns ::
        ON SUCCESS =>
        Dictionary with 2 keys:
            session_cookie: bytes
            expires: datetime.datetime
        NOTE: Don't forget to set the session_cookie on the HttpResponse!
        ON FAILURE =>
        boolean False
    """
    id_token = data.get("idToken")
    expires_in = timedelta(days=5)

    try:
        session_cookie = auth.create_session_cookie(
            id_token=id_token, expires_in=expires_in, app=app
        )
        expires = datetime.now(timezone.utc) + expires_in
        return {"session_cookie": session_cookie, "expires": expires}
    except exceptions.FirebaseError:
        return False


def login(
    request: http.HttpRequest, email: str, password: str
) -> Optional[http.HttpRequest]:
    """
    Function to log a user in and set the appropriate cookies.

    Arguments:
        request
        email
        password

    Returns:
        A modified Request object; use this request object while redirecting to a new page.
    """
    auth_data = authenticate_user(email, password)

    if not auth_data:
        raise AuthenticationError("User could not be authenticated")

    cookie = create_session_cookie(auth_data)

    if cookie:
        request.session["firebase-session-cookie"] = cookie
        request.session.set_expiry(cookie["expires"])
        return request
    else:
        raise AuthenticationError("User session cookie could not be made")


def check_logged_in(request: http.HttpRequest) -> Union[dict, bool]:
    """
    Checks whether a user is signed in (on Firebase, with email and password).

    Returns :
        The validated user details if True, else `bool` False.
    """
    firebase_session_cookie = request.session.get(
        "firebase-session-cookie"
    )  # the dict returned by create_session_cookie

    if not firebase_session_cookie:
        return False

    try:
        session_cookie_string = firebase_session_cookie.get("session_cookie")
        val = auth.verify_session_cookie(session_cookie_string, check_revoked=True)
        return val
    except auth.InvalidSessionCookieError:
        return False


def delete_session_cookie(request: http.HttpRequest) -> None:
    """
    Clears the session cookie. Meant to be used on sign out.

    Arguments:
        request: Request
    """
    firebase_session_cookie = request.session.get("firebase-session-cookie")
    session_cookie_string = firebase_session_cookie.get("session_cookie")
    try:
        decoded_claims = auth.verify_session_cookie(
            session_cookie_string, check_revoked=True
        )
        auth.revoke_refresh_tokens(decoded_claims["sub"])
    except auth.InvalidSessionCookieError:
        raise AuthenticationError("Tried to revoke an invalid session cookie")


def logout(request: HttpRequest) -> HttpRequest:
    """
    Deletes a user's session cookie and returns the request.

    Arguments:
        request
    Returns:
        A modified Request object; use this request object while redirecting to a new page.
    """
    delete_session_cookie(request)
    return request


class User:
    """
    Represents a user of Pothos.
    """

    def __init__(self, id: str, username: str, email: str, currency: str) -> None:
        self.username = username
        self.id = id
        self.email = email
        self.currency = currency
        self._db_user = None

    @classmethod
    def create(
        cls, *, username: str, email: str, password: str, currency: str
    ) -> "User":
        """
        Creates a new user and saves their details to Firebase and our database.
        All arguments must be provided as keyword-arguments.

        Arguments:
            username
            email
            password

        Returns:
            A `User` object representing the specific user.
        """
        firebase_user = _create_user(
            app, username=username, email=email, password=password
        )

        if not firebase_user:
            raise ValueError("Firebase user creation failed")

        db_user = _save_user_to_db(firebase_user, currency)

        new_pothos_user = cls(firebase_user.uid, username, email, currency)  # type: ignore
        new_pothos_user._db_user = db_user

        return new_pothos_user

    @classmethod
    def retrieve(cls, uid: str) -> "User":
        """
        Retrieve an existing user's details from the database.
        """
        from_firebase = get_user(app, uid)
        from_db = _get_user_from_db(uid)

        obj = cls(
            username=from_firebase.display_name,  # type: ignore
            email=from_firebase.email,  # type: ignore
            id=uid,
            currency=from_db.currency,
        )

        obj._db_user = from_db

        return obj

    def get_transactions(self) -> QuerySet:
        """
        Retrieve the user's transactions from the database.
        """
        return models.User.transaction_set.all()  # type: ignore

    def create_transaction(
        self, transaction_type: str, amount: float, name: str, notes: Optional[str] = ""
    ) -> models.Transaction:
        """
        Create and save a new transaction for the user on the database.

        Arguments:
            transaction_type -> The type of transaction. Must be either "income" or "expenditure".
            amount
            name
            notes -> Any optional notes for the transaction.
        """
        tr = models.Transaction(
            user=self.id,
            transaction_type=transaction_type,
            amount=amount,
            transaction_time=datetime.utcnow(),
            name=name,
            notes=notes,
        )
        tr.save()
        return tr

    def update_transaction(
        self, transaction_id: int, **fields: Any
    ) -> models.Transaction:
        """
        Updates the transaction with the specified ID with the given fields.
        """
        tr = models.Transaction(id=transaction_id, **fields)
        tr.save()
        return tr

    def delete_transaction(self, transaction_id: int) -> None:
        """
        Deletes a transaction with the specified ID.
        """
        tr = models.User.transaction_set.get(pk=transaction_id)  # type: ignore
        tr.delete()


class AuthenticationError(Exception):
    """
    Exception raised for auth related issues.
    """

    pass


class UnauthenticatedError(Exception):
    """
    Exception raised when an unauthenticated user tries reaching
    a page that requires authentications.
    """

    pass


def authorized() -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(
            request: http.HttpRequest, *args: Any, **kwargs: Any
        ) -> http.HttpResponse:
            """
            Decorator that checks if a user is signed in.
            The decorator will inject two arguments:
                user: User -> The User object for the signed in user.
            """
            from_firebase = check_logged_in(request)

            if from_firebase:
                user = User.retrieve(from_firebase["uid"])  # type: ignore
                return func(request, user=user, *args, **kwargs)
            else:
                raise UnauthenticatedError("Not logged in.")

        return wrapper

    return decorator
