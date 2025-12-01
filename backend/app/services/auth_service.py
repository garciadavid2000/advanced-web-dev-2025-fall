from flask import url_for
from app.services.user_service import UserService
from datetime import datetime, timedelta


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

        # Store OAuth tokens for calendar integration
        if token:
            user.access_token = token.get("access_token")
            user.refresh_token = token.get("refresh_token")
            
            # Calculate token expiry (typically expires_in is in seconds)
            expires_in = token.get("expires_in", 3600)
            user.token_expiry = datetime.now() + timedelta(seconds=expires_in)
            
            UserService.update_user_tokens(user)

        return user