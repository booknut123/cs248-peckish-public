# auth.py
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session

def google_login():
    """Don't change this code!"""
    CLIENT_ID = st.secrets["google"]["client_id"]
    CLIENT_SECRET = st.secrets["google"]["client_secret"]
    REDIRECT_URI = st.secrets["google"]["redirect_uri"]

    AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
    SCOPE = "openid email profile"

    params = st.query_params

    # 🟢 Step 1: Handle Google redirect back with code + state
    if "code" in params and "state" in params and "access_token" not in st.session_state:
        code = params["code"]
        state = params["state"]

        # Restore OAuth session using returned state (from URL)
        oauth = OAuth2Session(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope=SCOPE,
            redirect_uri=REDIRECT_URI,
            state=state,
        )

        try:
            # Debugging code that Eni used to debug
            st.write("🔎 Received code:", code)
            st.write("🔎 Received state:", state)
            st.write("🔎 Full query params:", st.query_params)
            token = oauth.fetch_token(TOKEN_ENDPOINT, code=code)
            st.session_state["access_token"] = token["access_token"]
            st.query_params.clear()
            return True
        except Exception as e:
            st.error(f"Login failed: {e}")
            st.write("Query Params on failure:", params)  # 👈 Add this line
            st.query_params.clear()
            return False

    # 👤 Step 2: Not logged in → show login button with state in URL
    if "access_token" not in st.session_state:
        oauth = OAuth2Session(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scope=SCOPE,
            redirect_uri=REDIRECT_URI,
        )
        auth_url, _state = oauth.create_authorization_url(AUTH_ENDPOINT)

        st.sidebar.markdown(
            f"""
            <a href="{auth_url}" target="_self">
                <button style='padding:10px 20px;font-size:16px;background-color:#0b72b9;color:white;border:none;border-radius:5px;cursor:pointer;'>
                    Login with Google
                </button>
            </a>
            """,
            unsafe_allow_html=True,
        )
        return False

    # ✅ Already logged in
    return True
