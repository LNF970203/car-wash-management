import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.let_it_rain import rain

st.set_page_config(
    page_title="LN Motors - Premium Car Detailing",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

colored_header(
    label="🚗 LN Motors",
    description="Premium Car Detailing & Care Services",
    color_name="blue-70",
)

st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 1rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
    }
    .service-card {
        background: grey;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        transition: transform 0.3s ease;
    }
    .service-card:hover {
        transform: translateY(-5px);
    }
    .hero-text {
        font-size: 1.2rem;
        line-height: 1.6;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="main-header">
    <h1>Welcome to LN Motors</h1>
    <p class="hero-text">
        Experience the ultimate car care with our premium detailing services. 
        From basic washes to complete interior and exterior restoration, 
        we bring back the showroom shine to your vehicle.
    </p>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="service-card">
        <h3>🧼 Exterior Wash</h3>
        <p>Professional exterior cleaning with premium products to protect your car's paint and finish.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="service-card">
        <h3>✨ Interior Detailing</h3>
        <p>Deep cleaning and restoration of your vehicle's interior for a fresh, like-new experience.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="service-card">
        <h3>🛡️ Paint Protection</h3>
        <p>Advanced ceramic coating and paint protection films to preserve your car's beauty.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🌟 Why Choose LN Motors?")
    st.markdown("""
    - **Premium Products**: We use only the finest car care products
    - **Expert Technicians**: Trained professionals with years of experience
    - **Customer Satisfaction**: Your happiness is our top priority
    - **Convenient Service**: Flexible scheduling and quick turnaround
    """)

with col2:
    st.subheader("📞 Contact Us")
    st.info("""
    **Phone 01:** +94 773076238\n
    **Phone 02:** +94 717854574\n
    **Email:** thelnmotors@gmail.com\n
    **Hours:** Mon-Sun 9AM-6PM
    """)

st.markdown("---")

if not st.user.is_logged_in:
    st.markdown("### 🔐 Customer Portal")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Log in to Your Account", use_container_width=True, type="primary"):
            st.login()
else:
    st.success(f"👋 Welcome back, {st.user.name}!")
    
    col1, col2, col3 = st.columns(3)
    # add sales button
    with col1:
        if st.button("📅 Add Sales", use_container_width=True):
            st.switch_page("pages/00_Sales.py")
    with col2:
        if st.button("📋 Dashboard", use_container_width=True):
            st.switch_page("pages/01_Dashboard.py")
    with col3:
        if st.button("🚪 Log out", use_container_width=True):
            st.logout()