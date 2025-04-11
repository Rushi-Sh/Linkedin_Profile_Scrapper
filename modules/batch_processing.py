import streamlit as st
import pandas as pd
from io import StringIO
from datetime import datetime
from companies_details_extraction.hr_scraper import get_hr_profiles
from companies_details_extraction.email_predictor import predict_emails_from_profiles

def render_batch_processing():
    st.subheader("📦 Batch Process Companies")
    
    # File upload
    uploaded_file = st.file_uploader("📄 Upload CSV file with company names", type="csv")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        batch_designation = st.text_input("👥 Designation", "HR OR Recruiter", key="batch_designation")
    with col2:
        country = st.text_input("🌍 Country", "India", key="batch_country")
    with col3:
        state = st.text_input("🏙️ State", "Gujarat", key="batch_state")
    with col4:
        profiles_per_company = st.number_input("🎯 Profiles per Company", min_value=1, max_value=30, value=5)
    
    if uploaded_file and st.button("Process Companies", key="batch_process"):
        process_companies(uploaded_file, batch_designation, country, state, profiles_per_company)
        
    # Show sample CSV format
    st.markdown("""
    ### 📝 CSV Format Example:
    Upload a CSV file with company names in the first column:
    ```
    Company Name
    Microsoft
    Google
    Apple
    ```
    """)

def process_companies(uploaded_file, designation, country, state, profiles_per_company):
    # Read CSV file
    companies_df = pd.read_csv(uploaded_file)
    company_list = companies_df.iloc[:, 0].tolist()  # Assume first column contains company names
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Process companies with progress tracking
    all_results = {}
    for idx, company in enumerate(company_list):
        status_text.text(f"Processing {company}...")
        profiles = get_hr_profiles(company, profiles_per_company, designation, country, state)
        all_results[company] = profiles
        progress_bar.progress((idx + 1) / len(company_list))
    
    display_results(company_list, all_results)

def display_results(company_list, all_results):
    # Create results DataFrame
    results_data = []
    for company, profiles in all_results.items():
        for profile in profiles:
            results_data.append([company, profile])
    
    results_df = pd.DataFrame(results_data, columns=['Company', 'Profile URL'])
    
    # Display results
    st.success(f"✅ Processed {len(company_list)} companies")
    st.dataframe(
        results_df,
        column_config={
            "Company": st.column_config.TextColumn("Company", width="medium"),
            "Profile URL": st.column_config.LinkColumn("Profile URL", width="large")
        },
        hide_index=True,
        height=400
    )
    
    # Download results
    csv_buffer = StringIO()
    results_df.to_csv(csv_buffer, index=False)
    
    st.download_button(
        label="📥 Download All Results as CSV",
        data=csv_buffer.getvalue(),
        file_name=f"batch_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
    display_email_predictions(all_results)

def display_email_predictions(all_results):
    st.markdown("### 📧 Email Predictions")
    for company in all_results.keys():
        with st.expander(f"📧 Email Predictions for {company}"):
            # Try to determine company domain
            company_domain = f"{company.lower().replace(' ', '')}.com"
            
            # Manual domain input
            manual_domain = st.text_input(
                "🔤 Enter company domain",
                value=company_domain,
                key=f"batch_domain_{company}"
            )
            
            if st.button("Generate Predictions", key=f"batch_predict_{company}"):
                generate_email_predictions(company, manual_domain, all_results[company])

def generate_email_predictions(company, domain, profiles):
    with st.spinner("🔮 Predicting email formats..."):
        email_df = predict_emails_from_profiles(profiles, domain)
    
    if not email_df.empty:
        st.success(f"✨ Generated predictions for {company}")
        st.dataframe(
            email_df,
            column_config={
                "Profile URL": st.column_config.LinkColumn("Profile URL", width="large"),
                "Predicted Email": st.column_config.TextColumn("Predicted Email", width="medium"),
                "Company Domain": st.column_config.TextColumn("Company Domain", width="medium")
            },
            hide_index=True,
            height=200
        )
        
        # Download button for email predictions
        email_csv_buffer = StringIO()
        email_df.to_csv(email_csv_buffer, index=False)
        st.download_button(
            label="📥 Download Email Predictions",
            data=email_csv_buffer.getvalue(),
            file_name=f"batch_email_predictions_{company}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            key=f"batch_download_{company}"
        )
    else:
        st.warning("Could not generate email predictions for this company.")
    
    display_email_patterns()

def display_email_patterns():
    with st.expander("ℹ️ Email Format Patterns"):
        st.info("Email formats are predicted based on common patterns:")
        st.markdown("- First letter of first name + last name (jsmith@domain.com)")
        st.markdown("- First name dot last name (john.smith@domain.com)")
        st.markdown("- First name underscore last name (john_smith@domain.com)")
        st.markdown("- First name + first letter of last name (johns@domain.com)")
        st.markdown("- First name only (john@domain.com)")
        st.markdown("- First initial dot last name (j.smith@domain.com)")