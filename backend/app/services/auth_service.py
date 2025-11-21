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
        userinfo = google.get("oauth2/v2/userinfo").json()

        google_id = userinfo.get("id")
        email = userinfo.get("email")
        name = userinfo.get("name")
        picture = userinfo.get("picture")

        user = UserService.get_or_create_google_user(
            google_id=google_id,
            email=email,
            name=name,
            picture=picture,
        )

        return user