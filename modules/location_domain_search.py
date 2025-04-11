import streamlit as st
import pandas as pd
from io import StringIO
from datetime import datetime
from companies_details_extraction.company_scraper import get_linkedin_company_links, extract_company_name_from_url
from companies_details_extraction.hr_scraper import get_hr_profiles
from companies_details_extraction.email_predictor import extract_company_domain, predict_emails_from_profiles

def on_form_change(key):
    def callback():
        st.session_state.form_state[key] = st.session_state[f"{key}_input"]
    return callback

def render_location_domain_search():
    location = st.text_input(
        "📍 Location",
        value=st.session_state.form_state['location'],
        key="location_domain_location_input",
        on_change=on_form_change("location")
    )
    
    domain = st.text_input(
        "💼 Domain",
        value=st.session_state.form_state['domain'],
        key="location_domain_domain_input",
        on_change=on_form_change("domain")
    )
    
    designation = st.text_input(
        "👤 Designation",
        value=st.session_state.form_state['direct_designation'],
        key="location_domain_designation_input",
        on_change=on_form_change("direct_designation")
    )
    
    country = st.text_input(
        "🌍 Country",
        value=st.session_state.form_state['country'],
        key="location_domain_country_input",
        on_change=on_form_change("country")
    )
    
    state = st.text_input(
        "🏙️ State",
        value=st.session_state.form_state['state'],
        key="location_domain_state_input",
        on_change=on_form_change("state")
    )
    
    num_companies = st.number_input(
        "🏢 Number of Companies",
        min_value=1,
        max_value=50,
        value=10,
        key="location_domain_num_companies_input",
        on_change=on_form_change("num_companies")
    )
    
    if st.button("Search Companies"):
        with st.spinner("🔍 Searching for LinkedIn company links..."):
            company_links = get_linkedin_company_links(location, domain, num_companies)
            st.session_state.companies = {extract_company_name_from_url(link): link for link in company_links}
            st.session_state.designation = designation
            st.session_state.location = location
            st.session_state.domain = domain
    
    if st.session_state.companies:
        st.success(f"🎯 Found {len(st.session_state.companies)} companies")

        st.subheader("📋 Found Companies")
        csv_buffer = StringIO()
        companies_df = pd.DataFrame(
            [[name, url] for name, url in st.session_state.companies.items()],
            columns=['Company Name', 'LinkedIn URL']
        )
        companies_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Download Company URLs as CSV",
            data=csv_buffer.getvalue(),
            file_name=f"company_urls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
        st.dataframe(
            companies_df,
            column_config={
                "Company Name": st.column_config.TextColumn("Company Name", width="medium"),
                "LinkedIn URL": st.column_config.LinkColumn("LinkedIn URL", width="large")
            },
            hide_index=True,
            height=300
        )

        st.markdown("### 🎯 Select Companies")
        available_companies = list(st.session_state.companies.keys())
        
        if 'selected_companies' not in st.session_state:
            st.session_state.selected_companies = available_companies[:5]
        else:
            st.session_state.selected_companies = [
                company for company in st.session_state.selected_companies 
                if company in available_companies
            ]

        selected_companies = st.multiselect(
            "Choose companies to find HR profiles:",
            options=available_companies,
            default=st.session_state.selected_companies
        )

        if 'profiles_per_company' not in st.session_state:
            st.session_state.profiles_per_company = 5

        profiles_per_company = st.number_input(
            "👥 Profiles per Company", 
            min_value=1, 
            max_value=30, 
            value=st.session_state.profiles_per_company
        )

        if selected_companies:
            if st.button("Find HR Profiles"):
                st.session_state.selected_companies = selected_companies
                st.session_state.profiles_per_company = profiles_per_company
                st.session_state.find_profiles_triggered = True

    if st.session_state.get("find_profiles_triggered", False):
        display_hr_profiles(
            st.session_state.selected_companies,
            st.session_state.profiles_per_company,
            st.session_state.form_state['direct_designation'],
            st.session_state.form_state['country'],
            st.session_state.form_state['state']
        )

def display_hr_profiles(selected_companies, profiles_per_company, designation, country, state):
    results_container = st.container()

    with st.spinner("🔍 Finding HR profiles for selected companies..."):
        all_profiles = {}
        progress_bar = st.progress(0)

        for idx, company in enumerate(selected_companies):
            profiles = get_hr_profiles(company, profiles_per_company, designation, country, state)
            all_profiles[company] = profiles
            progress_bar.progress((idx + 1) / len(selected_companies))

        st.session_state.profiles = all_profiles

        with results_container:
            display_results_and_predictions(selected_companies, all_profiles)

def display_results_and_predictions(selected_companies, all_profiles):
    st.success(f"✨ Found HR profiles for {len(selected_companies)} companies")

    results_data = []
    for company, profiles in all_profiles.items():
        for profile in profiles:
            results_data.append([company, profile])

    if results_data:
        results_df = pd.DataFrame(results_data, columns=['Company', 'Profile URL'])
        st.dataframe(
            results_df,
            column_config={
                "Company": st.column_config.TextColumn("Company", width="medium"),
                "Profile URL": st.column_config.LinkColumn("Profile URL", width="large")
            },
            hide_index=True,
            height=400
        )

        csv_buffer = StringIO()
        results_df.to_csv(csv_buffer, index=False)
        st.download_button(
            label="📥 Download HR Profiles as CSV",
            data=csv_buffer.getvalue(),
            file_name=f"hr_profiles_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

        display_email_predictions(selected_companies, all_profiles)

def display_email_predictions(selected_companies, all_profiles):
    st.markdown("### 📧 Predict Email Formats")
    for company in selected_companies:
        company_url = st.session_state.companies.get(company, "")
        company_domain = extract_company_domain(company_url)

        if company_domain:
            with st.expander(f"📧 Email Predictions for {company}"):
                process_email_predictions(company, all_profiles[company], company_domain)

def process_email_predictions(company, profiles, domain):
    predicted_emails = predict_emails_from_profiles(profiles, domain)
    for profile_url, email in predicted_emails.items():
        st.markdown(f"- [{profile_url}]({profile_url}) ➝ `{email}`")
