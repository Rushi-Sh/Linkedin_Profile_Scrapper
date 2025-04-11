import streamlit as st
import pandas as pd
import io
from datetime import datetime
from companies_details_extraction.hr_scraper import get_hr_profiles
from companies_details_extraction.email_predictor import predict_emails_from_profiles, extract_company_domain

def on_form_change(key):
    def callback():
        if f"{key}_input" in st.session_state:
            st.session_state.form_state[key] = st.session_state[f"{key}_input"]
    return callback

def render_direct_company_search():
    # Initialize input fields in session state if they don't exist
    input_keys = ['company_name', 'direct_designation', 'country', 'state', 'num_profiles']
    for key in input_keys:
        if f"{key}_input" not in st.session_state:
            st.session_state[f"{key}_input"] = st.session_state.form_state[key]

    company_name = st.text_input(
        "🏢 Enter Company Name",
        value=st.session_state.form_state['company_name'],
        key="company_name_input",
        on_change=on_form_change("company_name")
    )
    
    direct_designation = st.text_input(
        "👤 Designation",
        value=st.session_state.form_state['direct_designation'],
        key="direct_search_designation_input",
        on_change=on_form_change("direct_designation")
    )
    
    col1, col2 = st.columns(2)
    with col1:
        country = st.text_input(
            "🌍 Country",
            value=st.session_state.form_state['country'],
            key="direct_search_country_input",
            on_change=on_form_change("country")
        )
    with col2:
        state = st.text_input(
            "🏙️ State",
            value=st.session_state.form_state['state'],
            key="direct_search_state_input",
            on_change=on_form_change("state")
        )
    
    num_profiles = st.number_input(
        "👥 Number of Profiles",
        min_value=1,
        max_value=30,
        value=st.session_state.form_state['num_profiles'],
        key="direct_search_num_profiles_input",
        on_change=on_form_change("num_profiles")
    )
    
    if st.button("Find Profiles", key='direct_search'):
        handle_direct_search(company_name, direct_designation, country, state, num_profiles)

def handle_direct_search(company_name, designation, country, state, num_profiles):
    if company_name:
        with st.spinner(f"🔍 Searching for {designation} profiles..."):
            st.session_state.profiles = get_hr_profiles(company_name, num_profiles, designation=designation, country=country, state=state)
            
        if st.session_state.profiles:
            display_search_results(company_name, designation)
        else:
            st.warning("No HR profiles found.")
    else:
        st.warning("Please enter a company name.")

def display_search_results(company_name, designation):
    st.success(f"✨ Found {len(st.session_state.profiles)} {designation} profiles")
    
    # Display profiles DataFrame
    profiles_df = pd.DataFrame(
        [[company_name, profile] for profile in st.session_state.profiles],
        columns=['Company', 'Profile URL']
    )
    st.dataframe(
        profiles_df,
        column_config={
            "Company": st.column_config.TextColumn("Company", width="medium"),
            "Profile URL": st.column_config.LinkColumn("Profile URL", width="large")
        },
        hide_index=True,
        height=300
    )
    
    # Download button
    csv_buffer = io.StringIO()
    profiles_df.to_csv(csv_buffer, index=False)
    
    company_name_clean = company_name.replace(" ", "_").lower()
    st.download_button(
        label="📥 Download HR Profiles as CSV",
        data=csv_buffer.getvalue(),
        file_name=f"hr_profiles_{company_name_clean}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
    display_email_predictions(company_name)

def display_email_predictions(company_name):
    st.markdown("### 📧 Predict Email Formats")
    
    if st.session_state.profiles:
        company_url = ""
        if hasattr(st.session_state, 'companies') and st.session_state.companies is not None:
            company_url = st.session_state.companies.get(company_name, "")
        company_domain = extract_company_domain(company_url) if company_url else ""
        
        with st.expander("📧 Email Predictions", expanded=True):
            handle_email_predictions(company_name, company_domain)

def handle_email_predictions(company_name, company_domain):
    company_name_clean = company_name.replace(" ", "_").lower()
    
    if company_domain:
        predict_emails_with_domain(company_name_clean, company_domain)
    else:
        handle_manual_domain_input(company_name_clean)

def predict_emails_with_domain(company_name_clean, domain):
    with st.spinner("🔮 Predicting email formats..."):
        email_df = predict_emails_from_profiles(st.session_state.profiles, domain)
        display_email_results(email_df, company_name_clean)
        display_manual_domain_update(domain)

def handle_manual_domain_input(company_name_clean):
    st.warning("Could not determine company domain for email prediction.")
    manual_domain = st.text_input("🔤 Enter company domain manually", placeholder="example.com")
    if manual_domain and st.button("Generate Predictions"):
        with st.spinner("🔮 Predicting email formats..."):
            email_df = predict_emails_from_profiles(st.session_state.profiles, manual_domain)
            display_email_results(email_df, company_name_clean)

def display_email_results(email_df, company_name_clean):
    if not email_df.empty:
        st.success(f"✨ Generated predictions")
        st.dataframe(
            email_df,
            column_config={
                "Profile URL": st.column_config.LinkColumn("Profile URL", width="large"),
                "Predicted Email": st.column_config.TextColumn("Predicted Email", width="medium"),
                "Company Domain": st.column_config.TextColumn("Company Domain", width="medium")
            },
            hide_index=True,
            height=300
        )
        
        # Download button for email predictions
        email_csv_buffer = io.StringIO()
        email_df.to_csv(email_csv_buffer, index=False)
        st.download_button(
            label="📥 Download Email Predictions",
            data=email_csv_buffer.getvalue(),
            file_name=f"email_predictions_{company_name_clean}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

def display_manual_domain_update(current_domain):
    st.markdown("### 🔄 Update Domain")
    manual_domain = st.text_input("🔤 Enter company domain manually", value=current_domain)
    
    if manual_domain != current_domain and st.button("Update Predictions"):
        with st.spinner("🔮 Predicting email formats with new domain..."):
            email_df = predict_emails_from_profiles(st.session_state.profiles, manual_domain)
            if not email_df.empty:
                st.success(f"✨ Updated predictions with new domain")
                st.dataframe(
                    email_df,
                    column_config={
                        "Profile URL": st.column_config.LinkColumn("Profile URL", width="large"),
                        "Predicted Email": st.column_config.TextColumn("Predicted Email", width="medium"),
                        "Company Domain": st.column_config.TextColumn("Company Domain", width="medium")
                    },
                    hide_index=True,
                    height=300
                )

# Remove the update_analytics function at the end of the file