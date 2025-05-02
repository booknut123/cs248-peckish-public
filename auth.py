# Prof Eni's code

import streamlit as st
import requests

def google_login():
    """Manual OAuth login with a working Google Auth URL."""
    CLIENT_ID = st.secrets["google"]["client_id"]
    REDIRECT_URI = st.secrets["google"]["redirect_uri"]
    SCOPE = "openid email profile"
    AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"

    params = st.query_params

    # Step 1: Handle callback
    if "code" in params and "state" in params and "access_token" not in st.session_state:
        code = params["code"]

        try:
            response = requests.post(
                TOKEN_ENDPOINT,
                data={
                    "code": code,
                    "client_id": CLIENT_ID,
                    "client_secret": st.secrets["google"]["client_secret"],
                    "redirect_uri": REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                timeout=10,
            )
            response.raise_for_status()
            token = response.json()
            st.session_state["access_token"] = token["access_token"]
            st.query_params.clear()
            return True
        except Exception as e:
            st.error(f"Login failed: {e}")
            st.query_params.clear()
            return False

    # Step 2: Show login button with working link
    if "access_token" not in st.session_state:
        auth_url = (
            f"{AUTH_ENDPOINT}?"
            f"client_id={CLIENT_ID}&"
            f"redirect_uri={REDIRECT_URI}&"
            f"response_type=code&"
            f"scope={SCOPE.replace(' ', '%20')}&"
            f"access_type=offline&"
            f"prompt=consent&"
            f"state=streamlit_login"
        )

        #st.write(auth_url)
        st.sidebar.link_button("🔐 Login with Google", url=auth_url)
        return False

    return True

