# Remove pdfkit import
import streamlit as st
import json
import csv
from datetime import datetime
import os
import pandas as pd
from io import StringIO  
import io

from modules.location_domain_search import render_location_domain_search
from modules.direct_company_search import render_direct_company_search
from modules.batch_processing import render_batch_processing
from companies_details_extraction.company_scraper import get_linkedin_company_links, extract_company_name_from_url
from companies_details_extraction.hr_scraper import get_hr_profiles
from companies_details_extraction.email_predictor import extract_company_domain, predict_emails_from_profiles
from companies_details_extraction.job_search import search_all_platforms
from modules.job_search import render_job_search

# Initialize session state
if 'companies' not in st.session_state:
    st.session_state.companies = None
if 'selected_company' not in st.session_state:
    st.session_state.selected_company = None
if 'profiles' not in st.session_state:
    st.session_state.profiles = None
if 'designation' not in st.session_state:
    st.session_state.designation = None
if 'form_state' not in st.session_state:
    st.session_state.form_state = {
        'company_name': '',
        'direct_designation': 'HR OR Recruiter',
        'country': 'India',
        'state': 'Gujarat',
        'num_profiles': 10,
        'location': 'Ahmedabad',
        'domain': 'IT OR Software',
        'profiles_per_company': 5
    }

st.set_page_config(page_title="LinkedIn HR Scraper", layout="centered")
st.title("👥 LinkedIn HR Profile Scraper")

# Single tab navigation
search_mode = st.tabs([
    "🔍 Search by Location & Domain", 
    "🎯 Direct Company Search", 
    "📦 Batch Processing",
    "💼 Job Search"
])

with search_mode[0]:
    render_location_domain_search()

with search_mode[1]:
    render_direct_company_search()

with search_mode[2]:
    render_batch_processing()

with search_mode[3]:
    render_job_search()