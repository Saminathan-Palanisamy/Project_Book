import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000"

# --- Utility Functions ---
def login_user(username, password):
    url = f"{API_BASE_URL}/users/login"
    response = requests.post(url, data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Login failed: {response.json()['detail']}")
        return None

def register_user(username, email, password):
    url = f"{API_BASE_URL}/users/register"
    response = requests.post(url, json={"username": username, "email": email, "password": password})
    if response.status_code == 201:
        st.success("Registration successful! You can now login.")
        return True
    else:
        st.error(f"Registration failed: {response.json()['detail']}")
        return False

def get_current_user(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE_URL}/users/me", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Could not fetch user details. Token may be invalid or expired.")
        return None

def logout():
    keys = list(st.session_state.keys())
    for key in keys:
        del st.session_state[key]
    st.session_state["logged_out"] = True

# --- Streamlit Layout ---
st.set_page_config(page_title="Book App", page_icon="📚", layout="centered")
st.title("📚 Sajith Book Management")

# --- Show login/logout messages ---
if st.session_state.get("logged_out"):
    st.success("Logout successful!")
    del st.session_state["logged_out"]
    st.rerun()

if st.session_state.get("login_success"):
    st.success("Login successful!")
    del st.session_state["login_success"]

# --- Authentication Flow ---
if "access_token" not in st.session_state:

    # Toggle between login and register pages
    page = st.radio("Choose action", ["Login", "Register"])

    if page == "Login":
        st.subheader("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            token_data = login_user(username, password)
            if token_data:
                st.session_state["access_token"] = token_data["access_token"]
                st.session_state["login_success"] = True
                st.rerun()

    elif page == "Register":
        st.subheader("📝 Register")
        username = st.text_input("Choose Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        if st.button("Register"):
            if password != confirm_password:
                st.error("Passwords do not match!")
            else:
                success = register_user(username, email, password)
                if success:
                    st.info("You can now switch to the Login tab to access your account.")

else:
    # User is logged in, fetch details
    token = st.session_state["access_token"]
    user = get_current_user(token)

    if user:
        st.sidebar.header(f"👋 Welcome, {user['username']} ({user['role']})")
        st.sidebar.button("Logout", on_click=logout)

        st.write("✅ You are logged in!")
        st.write("### Your Profile")
        st.json(user)

        if user["role"] == "admin":
            st.success("You have admin privileges!")
        elif user["role"] == "vendor":
            st.info("You have vendor access.")
        else:
            st.write("You are a normal user.")
