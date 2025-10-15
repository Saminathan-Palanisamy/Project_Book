import streamlit as st
import requests

API_BASE_URL = "http://127.0.0.1:8000"

# --- Utility Functions ---
def login_user(username, password):
    url = f"{API_BASE_URL}/users/login"
    response = requests.post(url, data={"username": username, "password": password})
    try:
        resp_json = response.json()
    except Exception:
        st.error(f"Login failed. Status code: {response.status_code}, Response: {response.text}")
        return None

    if response.status_code == 200:
        return resp_json
    else:
        st.error(f"Login failed: {resp_json.get('detail', response.text)}")
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


def get_all_users(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_BASE_URL}/users/all", headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Could not fetch users. Permission denied or token expired.")
        return []


def approve_vendor(token, vendor_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_BASE_URL}/users/approve_vendor/{vendor_id}", headers=headers)
    return response.status_code == 200


def reject_vendor(token, vendor_id):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{API_BASE_URL}/users/reject_vendor/{vendor_id}", headers=headers)
    return response.status_code == 200


# --- Streamlit Layout ---
st.set_page_config(page_title="Book App", page_icon="📚", layout="centered")
st.title("📚 Sajith Book Management")

# --- Show login/logout messages ---
if st.session_state.get("logged_out"):
    st.toast("Logout successful!")
    del st.session_state["logged_out"]

if st.session_state.get("login_success"):
    st.toast("Login successful!")
    del st.session_state["login_success"]

# --- Authentication Flow ---
if "access_token" not in st.session_state:
    page = st.radio("Choose action", ["Login", "Register"])

    if page == "Login":
        st.subheader("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        def handle_login():
            token_data = login_user(username, password)
            if token_data:
                st.session_state["access_token"] = token_data["access_token"]
                st.session_state["login_success"] = True

        st.button("Login", on_click=handle_login)

    elif page == "Register":
        st.subheader("📝 Register")
        username = st.text_input("Choose Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        def handle_register():
            if password != confirm_password:
                st.error("Passwords do not match!")
            else:
                success = register_user(username, email, password)
                if success:
                    st.info("You can now switch to the Login tab to access your account.")

        st.button("Register", on_click=handle_register)

else:
    token = st.session_state["access_token"]
    user = get_current_user(token)

    if user:
        st.sidebar.header(f"👋 Welcome, {user['username']} ({user['role']})")
        st.sidebar.button("Logout", on_click=logout)

        st.write("✅ You are logged in!")
        st.write("### Your Profile")
        st.json(user)

        headers = {"Authorization": f"Bearer {token}"}

        # --- Admin Dashboard ---
        if user["role"] == "admin":
            st.subheader("🛠 Admin Dashboard")
            st.success("You have admin privileges!")

            st.write("### All Users")
            users_list = get_all_users(token)
            for u in users_list:
                st.write(f"{u['id']}: {u['username']} ({u['role']})")

            st.write("### Pending Vendor Requests")
            pending_vendors = []
            for u in users_list:
                resp = requests.get(f"{API_BASE_URL}/users/vendor_profile/{u['id']}", headers=headers)
                if resp.status_code == 200:
                    vp = resp.json()
                    if vp.get("verified") == "pending":
                        pending_vendors.append({**u, **vp})

            if pending_vendors:
                for vendor in pending_vendors:
                    st.write(f"{vendor['username']} - {vendor.get('business_name', 'No business name')}")
                    col1, col2 = st.columns(2)

                    def handle_approve(v_id=vendor['id'], v_name=vendor['username']):
                        if approve_vendor(token, v_id):
                            st.toast(f"{v_name} approved!")

                    def handle_reject(v_id=vendor['id'], v_name=vendor['username']):
                        if reject_vendor(token, v_id):
                            st.toast(f"{v_name} rejected!")

                    col1.button(f"Approve {vendor['username']}", key=f"approve_{vendor['id']}", on_click=handle_approve)
                    col2.button(f"Reject {vendor['username']}", key=f"reject_{vendor['id']}", on_click=handle_reject)
            else:
                st.info("No pending vendor requests.")

        # --- Vendor / User Section ---
        else:
            st.write("You are a normal user.")

            vendor_resp = requests.get(f"{API_BASE_URL}/users/vendor_profile/{user['id']}", headers=headers)

            if vendor_resp.status_code == 200:
                vendor_data = vendor_resp.json()
                verified_status = vendor_data.get("verified", "unknown")
                business_name = vendor_data.get("business_name", "N/A")

                if verified_status == "pending":
                    st.info(f"🕒 Your vendor registration for '{business_name}' has been sent for admin approval.")
                elif verified_status == "approved":
                    st.success(f"✅ Your vendor profile '{business_name}' is approved!")
                elif verified_status == "rejected":
                    st.error(f"❌ Your vendor registration for '{business_name}' was rejected by admin.")

                    st.subheader("🛒 Reapply as Vendor")
                    if "reapply_name" not in st.session_state:
                        st.session_state["reapply_name"] = business_name

                    business_name_retry = st.text_input("Business Name", value=st.session_state["reapply_name"])

                    def handle_reapply():
                        response = requests.post(
                            f"{API_BASE_URL}/users/register_vendor",
                            json={"business_name": business_name_retry, "force_reapply": True},
                            headers=headers
                        )
                        if response.status_code == 200:
                            st.success(f"✅ '{business_name_retry}' sent for approval to admin.")
                        else:
                            st.error(f"Failed: {response.json().get('detail', response.text)}")

                    st.button("Register as Vendor Again", on_click=handle_reapply)

            else:
                st.subheader("🛒 Become a Vendor")
                business_name = st.text_input("Business Name")

                def handle_register_vendor():
                    response = requests.post(
                        f"{API_BASE_URL}/users/register_vendor",
                        json={"business_name": business_name},
                        headers=headers
                    )
                    if response.status_code == 200:
                        st.success(f"✅ '{business_name}' sent for approval to admin.")
                    else:
                        st.error(f"Failed: {response.json().get('detail', response.text)}")

                st.button("Register as Vendor", on_click=handle_register_vendor)
