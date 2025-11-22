from flask import url_for
from app.services.user_service import UserService


class AuthService:

    @staticmethod
    def get_google_login_url(google):
        redirect_uri = url_for("auth.google_callback", _external=True)
        return google.authorize_redirect(redirect_uri)

    @staticmethod
    def handle_google_callback(google):
        token = google.authorize_access_token()
        userinfo = google.userinfo()

        print(userinfo)

        google_id = userinfo.get("sub")
        email = userinfo.get("email")
        name = userinfo.get("name")

        user = UserService.get_or_create_google_user(
            google_id=google_id,
            email=email,
            name=name
        )

        return user