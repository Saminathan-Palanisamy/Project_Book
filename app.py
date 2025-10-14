# app.py
import streamlit as st
import requests

BASE_URL = "http://127.0.0.1:8000"

# ---------------- Session state ----------------
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "role" not in st.session_state:
    st.session_state.role = None

# ---------------- Helpers ----------------
def get_headers():
    """Return headers with Authorization token if logged in"""
    return {"Authorization": f"Bearer {st.session_state.token}"} if st.session_state.token else {}

def fetch_current_user():
    """Fetch logged-in user info from backend and store in session_state"""
    if st.session_state.token:
        try:
            response = requests.get(f"{BASE_URL}/users/me", headers=get_headers())
            if response.status_code == 200:
                user = response.json()
                st.session_state.user_id = user.get("id")
                st.session_state.role = user.get("role")
            else:
                st.error("Failed to fetch user info")
        except Exception as e:
            st.error(f"Error fetching user info: {e}")

# ---------------- Registration ----------------
def register():
    st.subheader("Register / Sign Up")
    username = st.text_input("Username", key="reg_user")
    email = st.text_input("Email", key="reg_email")
    password = st.text_input("Password", type="password", key="reg_pass")
    if st.button("Register"):
        payload = {"username": username, "email": email, "password": password}
        try:
            response = requests.post(f"{BASE_URL}/users/register", json=payload)
            if response.status_code == 201:
                st.success("Registration successful! You can now login.")
            else:
                st.error(f"Registration failed: {response.json().get('detail')}")
        except Exception as e:
            st.error(f"Registration error: {e}")

# ---------------- Login ----------------
def login():
    st.subheader("Login")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    if st.button("Login"):
        try:
            data = {"username": username, "password": password}
            response = requests.post(f"{BASE_URL}/users/login", data=data)
            if response.status_code == 200:
                token = response.json().get("access_token")
                st.session_state.token = token
                st.session_state.user = username
                fetch_current_user()
                st.success(f"Logged in as {username}")
            else:
                st.error(f"Login failed: {response.json().get('detail')}")
        except Exception as e:
            st.error(f"Login error: {e}")

# ---------------- Logout ----------------
def logout():
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.user_id = None
    st.session_state.role = None
    st.success("Logged out successfully")

# ---------------- Books ----------------
def list_books():
    st.subheader("Available Books")
    try:
        response = requests.get(f"{BASE_URL}/books/")
        if response.status_code == 200:
            books = response.json()
            for book in books:
                st.write(f"**{book['title']}** (ID: {book['id']}) by Author ID: {book.get('author_id', 'N/A')}")
        else:
            st.error("Failed to fetch books")
    except Exception as e:
        st.error(f"Error: {e}")

def buy_book():
    st.subheader("Buy Book")
    book_id = st.number_input("Book ID", min_value=1, step=1)
    quantity = st.number_input("Quantity", min_value=1, step=1)
    if st.button("Buy"):
        if not st.session_state.token:
            st.error("Please login first!")
            return
        payload = {"user_id": st.session_state.user_id, "book_id": book_id, "quantity": quantity}
        try:
            response = requests.post(f"{BASE_URL}/purchases/", json=payload, headers=get_headers())
            if response.status_code == 201:
                st.success("Purchase successful!")
            else:
                st.error(f"Purchase failed: {response.json().get('detail')}")
        except Exception as e:
            st.error(f"Error: {e}")

# ---------------- Admin / Vendor ----------------
def create_author():
    st.subheader("Create Author (Admin/Approved Vendor)")
    name = st.text_input("Author Name", key="author_name")
    bio = st.text_area("Bio", key="author_bio")
    if st.button("Create Author"):
        payload = {"name": name, "bio": bio}
        try:
            response = requests.post(f"{BASE_URL}/authors/", json=payload, headers=get_headers())
            if response.status_code == 201:
                st.success(f"Author '{name}' created!")
            else:
                st.error(f"Failed to create author: {response.json().get('detail')}")
        except Exception as e:
            st.error(f"Error: {e}")

def create_book():
    st.subheader("Create Book (Admin/Approved Vendor)")
    title = st.text_input("Book Title", key="book_title")
    author_id = st.number_input("Author ID", min_value=1, step=1)
    description = st.text_area("Description", key="book_desc")
    if st.button("Create Book"):
        payload = {"title": title, "author_id": author_id, "description": description}
        try:
            response = requests.post(f"{BASE_URL}/books/", json=payload, headers=get_headers())
            if response.status_code == 201:
                st.success(f"Book '{title}' created!")
            else:
                st.error(f"Failed to create book: {response.json().get('detail')}")
        except Exception as e:
            st.error(f"Error: {e}")

def manage_vendors():
    st.subheader("Vendor Approvals (Admin Only)")
    vendor_id = st.number_input("Vendor Profile ID", min_value=1, step=1)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Approve Vendor"):
            try:
                response = requests.post(f"{BASE_URL}/users/approve_vendor/{vendor_id}", headers=get_headers())
                if response.status_code == 200:
                    st.success(f"Vendor {vendor_id} approved")
                else:
                    st.error(f"Failed: {response.json().get('detail')}")
            except Exception as e:
                st.error(f"Error: {e}")
    with col2:
        if st.button("Reject Vendor"):
            try:
                response = requests.post(f"{BASE_URL}/users/reject_vendor/{vendor_id}", headers=get_headers())
                if response.status_code == 200:
                    st.success(f"Vendor {vendor_id} rejected")
                else:
                    st.error(f"Failed: {response.json().get('detail')}")
            except Exception as e:
                st.error(f"Error: {e}")

# ---------------- Main ----------------
st.title("📚 Sajith Books Management")

if not st.session_state.token:
    tab = st.radio("Choose Option", ["Login", "Register"])
    if tab == "Login":
        login()
    else:
        register()
else:
    st.write(f"Logged in as **{st.session_state.user}** (Role: {st.session_state.role})")
    if st.button("Logout"):
        logout()

    st.divider()
    list_books()
    st.divider()
    buy_book()

    if st.session_state.role in ["admin", "vendor"]:
        st.divider()
        create_author()
        st.divider()
        create_book()

    if st.session_state.role == "admin":
        st.divider()
        manage_vendors()
