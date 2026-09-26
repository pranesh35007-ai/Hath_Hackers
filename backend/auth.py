import os
import hashlib
import hmac
import streamlit as st

def _password(role):
    defaults = {
        "admin": "Admin@123",
        "analyst": "Analyst@123",
        "viewer": "Viewer@123",
    }
    return os.getenv(f"{role.upper()}_PASSWORD", defaults[role])

def _valid(role, password):
    return hmac.compare_digest(
        hashlib.sha256(password.encode()).hexdigest(),
        hashlib.sha256(_password(role).encode()).hexdigest()
    )

def login_screen():
    st.markdown("""
    <div class="login-card">
      <div class="login-brand">HATH_HACKERS</div>
      <h1>Enterprise AI Data Analyst</h1>
      <p>Secure workspace for business intelligence, statistics and AI-assisted decisions.</p>
    </div>
    """, unsafe_allow_html=True)

    with st.form("login"):
        role = st.selectbox("Role", ["admin", "analyst", "viewer"])
        name = st.text_input("Display name", value=role.title())
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Sign in", use_container_width=True)

    if submitted:
        if _valid(role, password):
            st.session_state.user = {"name": name.strip() or role.title(), "role": role}
            st.rerun()
        else:
            st.error("Invalid role or password.")
