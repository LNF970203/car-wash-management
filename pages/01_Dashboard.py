import streamlit as st
import os
import uuid
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from db_utils import get_recent_records


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

# Dashboard page
st.title("📊 Sales Dashboard")

# Date range selection
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start Date", value=datetime.now().date() - timedelta(days=30))
with col2:
    end_date = st.date_input("End Date", value=datetime.now().date())

# Fetch data
if st.button("Load Data", type="primary"):
    with st.spinner("Fetching sales data..."):
        response = get_recent_records(
            TABLE_NAME,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        print("Response:", response)
        if response['success']:
            df = response['data']
            if df.empty:
                st.warning("No sales data found for the selected period.")
            else:
                # take a cop of the data
                df_copy = df.copy()
                # drop the sale id column
                df_copy = df_copy.drop(columns=['sale_id'])
                st.dataframe(df_copy)
                # Calculate metrics
                total_sales = len(df)
                total_revenue = df['price'].sum()
                avg_sale_value = df['price'].mean()
                latest_sale_date = df['service_date'].max().date()
                
                # Score cards
                col1, col2 = st.columns(2)
                col3, col4 = st.columns(2)
                
                with col1:
                    st.metric(
                        label="Total Sales",
                        value=f"{total_sales:,}",
                        delta=None
                    )
                
                with col2:
                    st.metric(
                        label="Total Revenue",
                        value=f"LKR {total_revenue:,.2f}",
                        delta=None
                    )
                
                with col3:
                    st.metric(
                        label="Average Sale Value",
                        value=f"LKR {avg_sale_value:,.2f}",
                        delta=None
                    )
                
                with col4:
                    st.metric(
                        label="Latest Sale Date",
                        value=latest_sale_date.strftime('%Y-%m-%d'),
                        delta=None
                    )
                
                st.markdown("---")
                
                # Sales by service type
                st.subheader("📈 Sales Analysis")
                
                # Expand services list for analysis
                services_expanded = df.explode('services')
                service_counts = services_expanded['services'].value_counts()
                service_revenue = services_expanded.groupby('services')['price'].sum()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Sales count by service type
                    fig1 = px.bar(
                        x=service_counts.index,
                        y=service_counts.values,
                        title="Number of Sales by Service Type",
                        labels={'x': 'Service Type', 'y': 'Number of Sales'},
                        color_discrete_sequence=['#667eea']
                    )
                    fig1.update_layout(showlegend=False)
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    # Revenue by service type
                    fig2 = px.pie(
                        values=service_revenue.values,
                        names=service_revenue.index,
                        title="Revenue Distribution by Service Type"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Sales over time
                st.subheader("📅 Sales Trend")
                
                # Daily sales
                daily_sales = df.groupby(df['service_date'].dt.date).agg({
                    'sale_id': 'count',
                    'price': 'sum'
                }).rename(columns={'sale_id': 'sales_count', 'price': 'daily_revenue'})
                
                fig3 = make_subplots(
                    rows=2, cols=1,
                    subplot_titles=('Daily Sales Count', 'Daily Revenue'),
                    vertical_spacing=0.1
                )
                
                fig3.add_trace(
                    go.Scatter(
                        x=daily_sales.index,
                        y=daily_sales['sales_count'],
                        mode='lines+markers',
                        name='Sales Count',
                        line=dict(color='#667eea')
                    ),
                    row=1, col=1
                )
                
                fig3.add_trace(
                    go.Scatter(
                        x=daily_sales.index,
                        y=daily_sales['daily_revenue'],
                        mode='lines+markers',
                        name='Revenue',
                        line=dict(color='#764ba2')
                    ),
                    row=2, col=1
                )
                
                fig3.update_layout(height=800, showlegend=False)
                st.plotly_chart(fig3, use_container_width=True)
                
                # Additional metrics
                st.subheader("📋 Additional Insights")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Most popular service
                    most_popular = service_counts.index[0]
                    st.info(f"🏆 Most Popular Service: {most_popular}")
                
                with col2:
                    # Highest revenue service
                    highest_revenue_service = service_revenue.index[0]
                    st.info(f"💰 Highest Revenue Service: {highest_revenue_service}")
                
                with col3:
                    # Best day
                    best_day = daily_sales['daily_revenue'].idxmax()
                    best_day_revenue = daily_sales['daily_revenue'].max()
                    st.info(f"⭐ Best Day: {best_day} (LKR {best_day_revenue:,.2f})")
                
                # Recent sales table
                st.subheader("📝 Recent Sales")
                
                # Format data for display
                display_df = df.copy()
                display_df['service_date'] = display_df['service_date'].dt.strftime('%Y-%m-%d')
                display_df['price'] = display_df['price'].apply(lambda x: f"LKR {x:,.2f}")
                display_df['services'] = display_df['services'].apply(lambda x: ', '.join(x))
                
                # Select columns to display
                display_columns = ['service_date', 'vehicle_number', 'services', 'price', 'customer_name']
                available_columns = [col for col in display_columns if col in display_df.columns]
                
                st.dataframe(
                    display_df[available_columns].head(10),
                    use_container_width=True,
                    hide_index=True
                )
                
        else:
            st.error(f"Error fetching data: {response['message']}")

