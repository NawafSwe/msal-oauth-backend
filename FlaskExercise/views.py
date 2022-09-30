from flask import render_template, redirect, request, session, url_for
from flask_login import current_user, login_user, logout_user, login_required
import msal
import uuid
from config import Config
from FlaskExercise import app
from FlaskExercise.models import User


@app.route("/")
@app.route("/home")
@login_required
def home():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    session["state"] = str(uuid.uuid4())
    # Note: Below will return None as an auth_url until you implement the function
    auth_url = _build_auth_url(scopes=Config.SCOPE, state=session["state"])
    return render_template("login.html", title="Sign In", auth_url=auth_url)


@app.route("/logout")
def logout():
    logout_user()  # Log out of Flask session
    if session.get("user"):  # Used MS Login
        # Wipe out user and its token cache from session
        session.clear()

        # And make sure to redirect from there back to the login page
        return redirect(
            Config.AUTHORITY
            + "/oauth2/v2.0/logout?post_logout_redirect_uri="
            + url_for("login", _external=True),
        )
    return redirect("login")


@app.route(
    Config.REDIRECT_PATH
)  # Its absolute URL must match your app's redirect_uri set in AAD
def authorized():
    if request.args.get("state") != session.get("state"):
        return redirect(url_for("home"))  # Failed, go back home
    if "error" in request.args:  # Authentication/Authorization failure
        return render_template("auth_error.html", result=request.args)

    if request.args.get("code"):
        cache = _load_cache()
        # acquire token from code
        result = _acquire_token_by_authorization_code(
            code=request.args.get("code"),
            scopes=Config.SCOPE,
            cache=cache,
        )
        if "error" in result:
            return render_template("auth_error.html", result=result)
        session["user"] = result.get("id_token_claims")
        # Note: In a real app, use the appropriate user's DB ID below,
        #   but here, we'll just log in with a fake user zero
        #   This is so flask login functionality works appropriately.
        user = User(0)
        login_user(user)
        _save_cache(cache)

    return redirect(url_for("home"))


def _load_cache():
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _build_msal_app(cache=None, authority=None):
    """
    building the clientConfidential app
    """
    return msal.ConfidentialClientApplication(
        client_id=Config.CLIENT_ID,
        client_credential=Config.CLIENT_SECRET,
        token_cache=cache,
        authority=authority,
    )


def _build_auth_url(authority=None, scopes=None, state=None):
    return _build_msal_app(
        authority=authority or Config.AUTHORITY
    ).get_authorization_request_url(
        scopes=scopes,
        state=state or str(uuid.uuid4()),
        redirect_uri="http://localhost:6700" + Config.REDIRECT_PATH,
    )


def _acquire_token_by_authorization_code(code, scopes, cache=None, redirect_uri=None):
    return _build_msal_app(
        authority=Config.AUTHORITY,
        cache=cache,
    ).acquire_token_by_authorization_code(
        code=code,
        scopes=scopes,
        redirect_uri="http://localhost:6700" + Config.REDIRECT_PATH,
    )


# def _logout(user):
#     cache = msal.SerializableTokenCache()
#     # invalidate idToken
#     cache.modify("IdToken", user)
