import streamlit as st
import requests
import pandas as pd
import socket

def get_api_url():
    try:
        socket.gethostbyname("api")
        return "http://api:8000"
    except socket.gaierror:
        return "http://localhost:8000"

API_URL = get_api_url()

st.set_page_config(page_title="Company Dashboard", page_icon="🏢", layout="wide")
st.title("🏢 Company Dashboard")

tab1, tab2 = st.tabs(["📋 Live Orders", "🍽️ Menu Management"])

with tab1:
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        st.header("Active Orders")
    with col2:
        if st.button("🔄 Refresh Orders"):
            st.rerun()
            
    try:
        response = requests.get(f"{API_URL}/orders")
        if response.status_code == 200:
            orders = response.json().get("orders", [])
            if not orders:
                st.info("No orders currently in the system!")
            else:
                for order in orders:
                    # Highlight pending orders
                    expanded = order['status'] == 'pending'
                    status_emoji = "⏳" if order['status'] == 'pending' else "✅" if order['status'] == 'completed' else "❌"
                    
                    with st.expander(f"{status_emoji} Order #{order['id']} - {order['status'].upper()}", expanded=expanded):
                        st.write(f"**AI Detected Intent:** `{order['customer_intent']}`")
                        st.write(f"**Customer Raw Message:** {order['order_text']}")
                        
                        cols = st.columns(3)
                        with cols[0]:
                            if st.button("Mark Completed", key=f"complete_{order['id']}", disabled=(order['status'] == 'completed')):
                                requests.put(f"{API_URL}/orders/{order['id']}", json={"status": "completed"})
                                st.rerun()
                        with cols[1]:
                            if st.button("Mark Cancelled", key=f"cancel_{order['id']}", disabled=(order['status'] == 'cancelled')):
                                requests.put(f"{API_URL}/orders/{order['id']}", json={"status": "cancelled"})
                                st.rerun()
        else:
            st.error("Failed to load orders from backend.")
    except Exception as e:
        st.error(f"Could not connect to API: {e}")

with tab2:
    col1, col2 = st.columns([0.6, 0.4])
    
    with col1:
        st.header("Current Menu")
        try:
            response = requests.get(f"{API_URL}/menu")
            if response.status_code == 200:
                menu = response.json().get("menu", [])
                if menu:
                    for item in menu:
                        with st.container():
                            c1, c2 = st.columns([0.8, 0.2])
                            with c1:
                                st.markdown(f"**{item['name']}** - ${item['price']}")
                                st.caption(item['description'])
                            with c2:
                                if st.button("🗑️ Delete", key=f"del_menu_{item['id']}"):
                                    requests.delete(f"{API_URL}/menu/{item['id']}")
                                    st.rerun()
                            st.divider()
                else:
                    st.info("Menu is empty in the database. Use the form to add dishes!")
            else:
                st.error("Failed to load menu.")
        except Exception as e:
            st.error(f"Could not connect to API: {e}")
            
    with col2:
        st.header("Add New Dish")
        with st.form("add_dish_form", clear_on_submit=True):
            name = st.text_input("Dish Name", placeholder="e.g. Classic Burger")
            desc = st.text_area("Description", placeholder="e.g. Beef patty with cheese")
            price = st.number_input("Price ($)", min_value=0.0, step=1.0, value=10.0)
            
            submitted = st.form_submit_button("➕ Add to Menu")
            if submitted:
                if name and desc:
                    new_item = {
                        "name": name,
                        "description": desc,
                        "price": price
                    }
                    res = requests.post(f"{API_URL}/menu", json=new_item)
                    if res.status_code == 200:
                        st.success("Dish added successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to add dish.")
                else:
                    st.warning("Please fill in both Name and Description.")

        st.markdown("---")
        st.header("Upload New PDF Menu")
        uploaded_file = st.file_uploader("Choose a menu PDF", type=["pdf"])
        if uploaded_file is not None:
            if st.button("🚀 Process & Import PDF Menu", use_container_width=True):
                with st.spinner("Parsing PDF with Vision AI... This may take a moment."):
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    try:
                        upload_res = requests.post(f"{API_URL}/menu/pdf/upload", files=files)
                        if upload_res.status_code == 200:
                            res_json = upload_res.json()
                            if "error" in res_json:
                                st.error(res_json["error"])
                            else:
                                st.success(res_json.get("message", "Uploaded!"))
                                st.rerun()
                        else:
                            st.error(f"Upload failed: status code {upload_res.status_code}")
                    except Exception as e:
                        st.error(f"Error during upload: {e}")

        st.markdown("---")
        st.header("Manage PDF Menus")
        try:
            list_res = requests.get(f"{API_URL}/menu/pdf")
            if list_res.status_code == 200:
                pdf_files = list_res.json().get("files", [])
                if not pdf_files:
                    st.info("No PDF menus uploaded yet.")
                else:
                    for filename in pdf_files:
                        col_name, col_btn = st.columns([0.7, 0.3])
                        clean_name = filename.replace(".pdf", "").replace("_", " ").title()
                        with col_name:
                            st.write(f"📄 **{clean_name}**")
                            st.caption(filename)
                        with col_btn:
                            if st.button("🗑️ Delete", key=f"del_pdf_{filename}", use_container_width=True):
                                del_res = requests.delete(f"{API_URL}/menu/pdf/{filename}")
                                if del_res.status_code == 200:
                                    st.success(f"Deleted {filename}!")
                                    st.rerun()
                                else:
                                    st.error("Failed to delete.")
            else:
                st.error("Failed to load PDF menu list.")
        except Exception as e:
            st.error(f"Could not connect to API: {e}")
