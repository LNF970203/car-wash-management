import streamlit as st
import os
import uuid
from decimal import Decimal

from db_utils import add_record


# get env name from secrets
ENV = st.secrets["aws"]["ENV"]

TABLE_NAME = f"{ENV}_sales"


# get admin emails
admin_emails = st.secrets["admin"]["ADMIN_USERS"]


if not st.user.is_logged_in:
    # error message saying to log in
    st.error("Please log in to access this page")
    st.stop()

if st.user.email not in admin_emails:
    # error message saying to log in
    st.error("You do not have access to this page")
    st.stop()

# sales page
st.title("Record Sales")

with st.form("sales_form"):
    st.subheader("Vehicle & Service Information")
    
    # Required fields
    vehicle_number = st.text_input(
        "Vehicle Number *", 
        placeholder="Enter vehicle registration number",
        help="Required field - Enter the complete vehicle number"
    )
    
    service_date = st.date_input(
        "Service Date *",
        help="Required field - Select the date of service",
        value="today"
    )
    
    price = st.number_input(
        "Price (LKR) *", 
        min_value=0.0, 
        step=100.0, 
        placeholder="Enter service price",
        help="Required field - Enter the total service price"
    )
    
    interior_type = st.multiselect(
        "Interior Type *", 
        options=["Full Interior", "Basic Interior", "Body Wash"],
        help="Required field - Select one or more service types"
    )
    
    st.markdown("---")
    st.subheader("Customer Information (Optional)")
    
    # Optional fields
    customer_name = st.text_input(
        "Customer Name", 
        placeholder="Enter customer name (optional)"
    )
    
    contact_number = st.text_input(
        "Contact Number", 
        placeholder="Enter contact number (optional)"
    )
    
    description = st.text_area(
        "Additional Description", 
        placeholder="Enter any additional notes or description (optional)",
        height=100
    )
    
    # Submit button
    submitted = st.form_submit_button("Record Sale", type="primary")
    
    if submitted:
        # Validation for required fields
        errors = []
        
        if not vehicle_number.strip():
            errors.append("Vehicle Number is required")
        
        if not service_date:
            errors.append("Service Date is required")
        
        if price <= 0:
            errors.append("Price must be greater than 0")
        
        if not interior_type:
            errors.append("At least one Interior Type must be selected")
        
        if errors:
            for error in errors:
                st.error(error)
        else:
            # Success message with all details
            with st.spinner("Record is saving......"):
                sale_id = str(uuid.uuid4())
                # add the records to database
                db_response = add_record(
                    TABLE_NAME,
                    sale_id, 
                    vehicle_number,
                    service_date.strftime('%Y-%m-%d'),
                    interior_type,
                    Decimal(price),
                    "success",
                    customer_name,
                    contact_number,
                    description

                )
                if db_response["success"]:
                    st.success("Sale recorded successfully!")
                else:
                    st.error(db_response["message"])
            
            st.markdown("### Sale Details:")
            st.markdown(f"**Vehicle Number:** {vehicle_number}")
            st.markdown(f"**Service Date:** {service_date.strftime('%Y-%m-%d')}")
            st.markdown(f"**Price:** LKR {price:,.2f}")
            st.markdown(f"**Services:** {', '.join(interior_type)}")
            
            if customer_name:
                st.markdown(f"**Customer Name:** {customer_name}")
            
            if contact_number:
                st.markdown(f"**Contact Number:** {contact_number}")
            
            if description:
                st.markdown(f"**Description:** {description}")

