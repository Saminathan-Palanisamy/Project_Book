import streamlit as st
import requests

API = "http://127.0.0.1:8000"

st.title("Sajith Books - Suma login pani pakuren")

if "token" not in st.session_state:
    st.session_state.token = None

with st.form("login"):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    submitted = st.form_submit_button("Login")
    if submitted:
        # Use form-encoded login? The API expects form for /users/login
        resp = requests.post(f"{API}/users/login", data={"username": username, "password": password})
        if resp.status_code == 200:
            st.session_state.token = resp.json()["access_token"]
            st.success("Logged in")
        else:
            st.error(f"Login failed: {resp.text}")

if st.session_state.token:
    st.write("You are logged in.")
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    # Example get user  (replace <user_id>)
    # r = requests.get(f"{API}/users/1", headers=headers)
    # st.write(r.json())
