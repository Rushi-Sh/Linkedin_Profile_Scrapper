# Remove pdfkit import
import streamlit as st
import json
import csv
from datetime import datetime
import os
import pandas as pd
from io import StringIO  # Add this import

from companies_details_extraction.company_scraper import get_linkedin_company_links, extract_company_name_from_url
from companies_details_extraction.hr_scraper import get_hr_profiles
from companies_details_extraction.company_insights import get_company_insights

# After imports and before session state initialization
def update_analytics(search_type, company, num_results):
    """Update analytics data in session state"""
    st.session_state.analytics_data['searches'].append({
        'date': datetime.now().date(),
        'type': search_type,
        'company': company
    })
    st.session_state.analytics_data['results'].append({
        'company': company,
        'num_results': num_results,
        'date': datetime.now().date()
    })

# Initialize session state
if 'companies' not in st.session_state:
    st.session_state.companies = None
if 'selected_company' not in st.session_state:
    st.session_state.selected_company = None
if 'profiles' not in st.session_state:
    st.session_state.profiles = None
if 'designation' not in st.session_state:
    st.session_state.designation = None
if 'search_templates' not in st.session_state:
    st.session_state.search_templates = {}
if 'analytics_data' not in st.session_state:
    st.session_state.analytics_data = {'searches': [], 'results': []}

st.set_page_config(page_title="LinkedIn HR Scraper", layout="centered")
st.title("👥 LinkedIn HR Profile Scraper")

# Single tab navigation
search_mode = st.tabs([
    "🔍 Search by Location & Domain", 
    "🎯 Direct Company Search", 
    "📦 Batch Processing",
    "📊 Analytics",
    "🏢 Company Insights",
    "📑 Search Templates"
])

with search_mode[0]:
    # Existing search by location and domain
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        location = st.text_input("📍 Location", "Ahmedabad")
    with col2:
        domain = st.text_input("💼 Domain", "IT OR Software")
    with col3:
        designation = st.text_input("👤 Designation", "HR OR Recruiter")
    # In the first tab (Search by Location & Domain)
    with col4:
        num_companies = st.number_input("🏢 Number of Companies", min_value=1, max_value=50, value=10, key="location_search_num")
    
    if st.button("Search Companies"):
        with st.spinner("🔍 Searching for LinkedIn company links..."):
            company_links = get_linkedin_company_links(location, domain, num_companies)
            st.session_state.companies = {extract_company_name_from_url(link): link for link in company_links}
            st.session_state.designation = designation

with search_mode[1]:
    # Direct company search
    company_name = st.text_input("🏢 Enter Company Name")
    direct_designation = st.text_input("👤 Designation", "HR OR Recruiter", key="direct_designation")
    num_profiles = st.number_input("👥 Number of Profiles", min_value=1, max_value=30, value=10, key="direct_search_num")
    
    if st.button("Find Profiles", key='direct_search'):
        if company_name:
            with st.spinner(f"🔍 Searching for {direct_designation} profiles..."):
                st.session_state.profiles = get_hr_profiles(company_name, num_profiles, designation=direct_designation)
                
            # In direct search:
            if st.session_state.profiles:
                update_analytics('direct', company_name, len(st.session_state.profiles))
                st.success(f"✨ Found {len(st.session_state.profiles)} {direct_designation} profiles")
                
                # Display profiles DataFrame
                st.subheader(f"👥 {direct_designation} Profiles")
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
                    height=300  # Fixed height for scrollable view
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
            else:
                st.warning("No HR profiles found.")
        else:
            st.warning("Please enter a company name.")

# Add custom CSS for dark mode styling
st.markdown("""
    <style>
    .company-link {
        background-color: #1E1E1E;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        border: 1px solid #333;
    }
    .profile-card {
        background-color: #2C2C2C;
        padding: 15px;
        border-radius: 8px;
        margin: 10px 0;
        border: 1px solid #404040;
    }
    .section-divider {
        margin: 30px 0;
        border-top: 1px solid #404040;
    }
    </style>
""", unsafe_allow_html=True)

# Display companies if they exist in session state
if st.session_state.companies:
    st.success(f"🎯 Found {len(st.session_state.companies)} companies")
    
    # Add a divider
    st.markdown("<div class='section-divider'></div>", unsafe_allow_html=True)
    
    # Companies display as DataFrame
    st.subheader("📋 Found Companies")
    companies_df = pd.DataFrame(
        [[name, url] for name, url in st.session_state.companies.items()],
        columns=['Company Name', 'LinkedIn URL']
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
    
   

# Remove the following section and continue with the next tab
with search_mode[2]:
    st.subheader("📦 Batch Process Companies")
    
    # File upload
    uploaded_file = st.file_uploader("📄 Upload CSV file with company names", type="csv")
    
    col1, col2 = st.columns(2)
    with col1:
        batch_designation = st.text_input("👥 Designation", "HR OR Recruiter", key="batch_designation")
    with col2:
        profiles_per_company = st.number_input("🎯 Profiles per Company", min_value=1, max_value=30, value=5)
    
    if uploaded_file and st.button("Process Companies", key="batch_process"):
        # Read CSV file
        companies_df = pd.read_csv(uploaded_file)
        company_list = companies_df.iloc[:, 0].tolist()  # Assume first column contains company names
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Process companies with progress tracking
        all_results = {}
        for idx, company in enumerate(company_list):
            status_text.text(f"Processing {company}...")
            profiles = get_hr_profiles(company, profiles_per_company, batch_designation)
            all_results[company] = profiles
            progress_bar.progress((idx + 1) / len(company_list))
        
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

# Add Analytics Dashboard
with search_mode[3]:
    st.subheader("📊 Analytics Dashboard")
    
    # Create columns for different metrics
    metric1, metric2, metric3 = st.columns(3)
    
    with metric1:
        total_searches = len(st.session_state.analytics_data['searches'])
        st.metric("Total Searches", total_searches)
    
    with metric2:
        total_profiles = sum(len(r) for r in st.session_state.analytics_data['results'])
        st.metric("Total Profiles Found", total_profiles)
    
    with metric3:
        avg_profiles = total_profiles / total_searches if total_searches > 0 else 0
        st.metric("Avg. Profiles per Search", f"{avg_profiles:.1f}")
    
    # Search history chart
    if st.session_state.analytics_data['searches']:
        search_df = pd.DataFrame(st.session_state.analytics_data['searches'])
        st.line_chart(search_df.groupby('date').size())
        
    # Results distribution
    st.subheader("Results Distribution by Company")
    if st.session_state.analytics_data['results']:
        results_df = pd.DataFrame(st.session_state.analytics_data['results'])
        st.bar_chart(results_df.groupby('company').size())

# Add Company Insights
with search_mode[4]:
    st.subheader("🏢 Company Insights")
    if st.session_state.selected_company:
        insights = get_company_insights(st.session_state.selected_company)
        if 'error' not in insights:
            st.markdown(f"### {st.session_state.selected_company} Insights")
            st.markdown("#### Company Overview")
            st.markdown(f"**Industry:** {insights['Company Overview'].get('Industry', 'N/A')}")
            st.markdown(f"**Size:** {insights['Company Overview'].get('Size', 'N/A')}")
            st.markdown(f"**Founded:** {insights['Company Overview'].get('Founding Year', 'N/A')}")
            st.markdown(f"**Headquarters:** {insights['Company Overview'].get('Headquarters', 'N/A')}")
            st.markdown("#### Key Products/Services")
            st.markdown(f"{insights.get('Key Products/Services', 'N/A')}")
            st.markdown("#### Employee Distribution")
            st.markdown(f"{insights.get('Employee Distribution', 'N/A')}")
            st.markdown("#### Recent Growth Metrics")
            st.markdown(f"{insights.get('Recent Growth Metrics', 'N/A')}")
            st.markdown("#### Key Achievements and Market Position")
            st.markdown(f"{insights.get('Key Achievements and Market Position', 'N/A')}")
        else:
            st.error(f"Error fetching insights: {insights['error']}")
    else:
        st.warning("Please select a company first.")
    
    company_search = st.text_input("Enter Company Name for Insights")
    if company_search and st.button("Get Insights"):
        with st.spinner("🔍 Gathering real-time company insights..."):
            insights = get_company_insights(company_search)
            
            if "error" not in insights:
                # Create tabs for different insight categories
                insight_tabs = st.tabs(["Overview", "Products & Services", "Employee Distribution", "Growth & Achievements"])
                
                with insight_tabs[0]:
                    st.markdown(f"""
                    ### {company_search} Overview
                    - **Industry**: {insights['Company Overview']['Industry']}
                    - **Company Size**: {insights['Company Overview']['Size']}
                    - **Founded**: {insights['Company Overview']['Founding Year']}
                    - **Headquarters**: {insights['Company Overview']['Headquarters']}
                    """)
                
                with insight_tabs[1]:
                    st.markdown("### Key Products/Services")
                    st.markdown(f"- {insights['Key Products/Services']}")
                
                with insight_tabs[2]:
                    # Employee distribution markdown
                    st.markdown("#### Employee Distribution")
                    st.markdown(f"- {insights['Employee Distribution']}")
                
                with insight_tabs[3]:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("#### Recent Growth Metrics")
                        if 'Recent Growth Metrics' in insights:
                            st.markdown(f"- {insights['Recent Growth Metrics']}")
                        else:
                            st.markdown("- N/A")
                    
                    with col2:
                        st.markdown("### Key Achievements")
                        if 'Key Achievements and Market Position' in insights:
                            st.markdown(f"- {insights['Key Achievements and Market Position']}")
                        else:
                            st.markdown("- N/A")
            else:
                st.error(f"Error: {insights['error']}")

# Add Search Templates
with search_mode[5]:
    st.subheader("📑 Search Templates")
    
    # Template creation
    with st.expander("➕ Create New Template"):
        template_name = st.text_input("Template Name")
        col1, col2 = st.columns(2)
        with col1:
            template_designation = st.text_input("Default Designation")
            template_location = st.text_input("Default Location")
        with col2:
            template_domain = st.text_input("Default Domain")
            template_num_profiles = st.number_input("Default Number of Profiles", 1, 30, 10, key="template_num")
        
        if st.button("Save Template"):
            if template_name:
                st.session_state.search_templates[template_name] = {
                    'designation': template_designation,
                    'location': template_location,
                    'domain': template_domain,
                    'num_profiles': template_num_profiles
                }
                st.success("Template saved!")
    
    # Template list and usage
    if st.session_state.search_templates:
        st.subheader("Saved Templates")
        selected_template = st.selectbox(
            "Select a template to use",
            list(st.session_state.search_templates.keys())
        )
        
        if selected_template and st.button("Use Template"):
            template = st.session_state.search_templates[selected_template]
            # Apply template values to session state
            st.session_state.designation = template['designation']
            st.session_state.location = template['location']
            st.session_state.domain = template['domain']
            st.session_state.num_profiles = template['num_profiles']
            st.success("Template applied! Switch to search tab to continue.")
