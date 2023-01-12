# This is based on Airflow's user password model

from typing import List

from flask import request
import flask_login
from flask_login import current_user
import jwt

from app.auth.utils import AuthUser, AuthenticationError, QuerybookLoginManager
from app.db import DBSession, with_session
from lib.logger import get_logger
from logic.user import create_user, get_user_by_name

LOG = get_logger(__file__)
login_manager = QuerybookLoginManager()


@with_session
def authenticate(session=None):
    """Authenticate a PasswordUser with the Bearer token

    :param session: An active SQLAlchemy session


    :raise AuthenticationError: if an error occurred
    :return: a PasswordUser
    """

    # Need not verify the token. Already verified at the network proxy layer
    bearer_token = request.headers.get("Authorization")
    if not bearer_token:
        raise AuthenticationError("Missing request headers")

    if bearer_token.count(" ") != 1:
        raise AuthenticationError("Invalid JWT")

    split_token: List[str] = bearer_token.split(" ")
    if split_token[0].lower() != "bearer":
        raise AuthenticationError("Invalid JWT")

    try:
        data = jwt.decode(split_token[1], options={"verify_signature": False})
    except Exception as e:
        raise AuthenticationError("Error parsing jwt") from e

    # Using the (uid)oid from azure as the username
    (username, email, fullname) = (data["uid"], data["upn"], data["name"])

    user = get_user_by_name(username, session=session)
    if not user:
        # create user if they do not exist
        user = create_user(username=username, email=email, fullname=fullname)
        LOG.info(f"First login for user {fullname}")

    return AuthUser(user)


def login_user_endpoint():
    if current_user.is_authenticated:
        return

    with DBSession() as session:
        user = authenticate(session=session)
        flask_login.login_user(user)

        return user


def init_app(app):
    login_manager.init_app(app)


def login(request):
    pass
