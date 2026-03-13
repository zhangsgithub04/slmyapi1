import os
import streamlit as st
import requests

API_BASE = os.getenv("API_BASE", "https://myapi1-pz44.onrender.com")
API_KEY = os.getenv("MY_API_KEY")

if not API_KEY:
    st.error("Missing MY_API_KEY environment variable")
    st.stop()

st.set_page_config(page_title="President UI", layout="wide")
st.title("President UI")

if "edit_id" not in st.session_state:
    st.session_state.edit_id = None


def api_headers():
    return {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json",
    }


def get_presidents():
    r = requests.get(
        f"{API_BASE}/presidents",
        headers=api_headers(),
        timeout=20,
    )
    r.raise_for_status()
    return r.json()


def create_president(firstname, lastname, birthdate):
    r = requests.post(
        f"{API_BASE}/presidents",
        json={
            "firstname": firstname,
            "lastname": lastname,
            "birthdate": birthdate or None,
        },
        headers=api_headers(),
        timeout=20,
    )
    return r


def update_president(president_id, firstname, lastname, birthdate):
    r = requests.patch(
        f"{API_BASE}/presidents/{president_id}",
        json={
            "firstname": firstname,
            "lastname": lastname,
            "birthdate": birthdate or None,
        },
        headers=api_headers(),
        timeout=20,
    )
    return r


def delete_president(president_id):
    r = requests.delete(
        f"{API_BASE}/presidents/{president_id}",
        headers=api_headers(),
        timeout=20,
    )
    return r


try:
    presidents = get_presidents()
except Exception as e:
    st.error(f"Could not load presidents: {e}")
    st.stop()

edit_row = None
if st.session_state.edit_id is not None:
    for row in presidents:
        if row["id"] == st.session_state.edit_id:
            edit_row = row
            break

st.subheader("Add / Edit President")

with st.form("president_form"):
    firstname = st.text_input(
        "First Name",
        value=edit_row["firstname"] if edit_row else ""
    )
    lastname = st.text_input(
        "Last Name",
        value=edit_row["lastname"] if edit_row else ""
    )
    birthdate = st.text_input(
        "Birthdate (YYYY-MM-DD)",
        value=edit_row["birthdate"] if edit_row and edit_row.get("birthdate") else ""
    )

    c1, c2 = st.columns(2)
    save = c1.form_submit_button("Update" if edit_row else "Create")
    clear = c2.form_submit_button("Clear")

if save:
    try:
        if st.session_state.edit_id is None:
            r = create_president(
                firstname.strip(),
                lastname.strip(),
                birthdate.strip(),
            )
        else:
            r = update_president(
                st.session_state.edit_id,
                firstname.strip(),
                lastname.strip(),
                birthdate.strip(),
            )

        if r.ok:
            st.success("Saved successfully")
            st.session_state.edit_id = None
            st.rerun()
        else:
            st.error(r.text)
    except Exception as e:
        st.error(f"Save failed: {e}")

if clear:
    st.session_state.edit_id = None
    st.rerun()

st.subheader("President List")

for row in presidents:
    c1, c2, c3, c4, c5, c6 = st.columns([1, 2, 2, 2, 1, 1])
    c1.write(row["id"])
    c2.write(row.get("firstname", ""))
    c3.write(row.get("lastname", ""))
    c4.write(row.get("birthdate", ""))

    if c5.button("Edit", key=f"edit_{row['id']}"):
        st.session_state.edit_id = row["id"]
        st.rerun()

    if c6.button("Delete", key=f"delete_{row['id']}"):
        try:
            r = delete_president(row["id"])
            if r.ok:
                st.success(f"Deleted {row['id']}")
                if st.session_state.edit_id == row["id"]:
                    st.session_state.edit_id = None
                st.rerun()
            else:
                st.error(r.text)
        except Exception as e:
            st.error(f"Delete failed: {e}")
