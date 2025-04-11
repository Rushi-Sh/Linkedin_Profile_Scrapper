import streamlit as st
import pandas as pd
from io import StringIO
from datetime import datetime
from companies_details_extraction.job_search import search_all_platforms

def render_job_search():
    st.subheader("💼 Job & Internship Search")
    
    col1, col2 = st.columns(2)
    with col1:
        job_title = st.text_input("🔍 Job Title/Keywords", "Software Developer", key="job_search_title")
        job_location = st.text_input("📍 Location", "Ahmedabad", key="job_search_location")
    
    with col2:
        search_type = st.radio(
            "Search Type",
            ["Jobs", "Internships", "Both"],
            horizontal=True,
            key="job_search_type"
        )
        num_results = st.number_input(
            "📊 Results per Platform",
            min_value=1,
            max_value=30,
            value=10,
            help="Number of results to fetch from each platform"
        )
    
    platforms = st.multiselect(
        "🌐 Select Platforms",
        ["LinkedIn", "Indeed", "Glassdoor", "Internshala"],
        default=["LinkedIn", "Indeed", "Glassdoor"],
        key="job_search_platforms"
    )
    
    if st.button("🔍 Search", key="job_search_button"):
        process_job_search(job_title, job_location, search_type, platforms, num_results)

def process_job_search(job_title, job_location, search_type, platforms, num_results):
    with st.spinner("🔍 Searching for opportunities across platforms..."):
        is_internship = search_type in ["Internships", "Both"]
        is_job = search_type in ["Jobs", "Both"]
        
        all_results = pd.DataFrame()
        
        if is_job:
            job_results = search_all_platforms(job_title, job_location, is_internship=False, limit=num_results)
            if not job_results.empty:
                job_results["Type"] = "Job"
                all_results = pd.concat([all_results, job_results])
        
        if is_internship:
            internship_results = search_all_platforms(job_title, job_location, is_internship=True, limit=num_results)
            if not internship_results.empty:
                internship_results["Type"] = "Internship"
                all_results = pd.concat([all_results, internship_results])
        
        display_search_results(all_results, platforms)

def display_search_results(all_results, platforms):
    if platforms and not all_results.empty:
        all_results = all_results[all_results["source"].isin(platforms)]
    
    if not all_results.empty:
        st.success(f"✨ Found {len(all_results)} opportunities")
        
        st.dataframe(
            all_results,
            column_config={
                "title": st.column_config.TextColumn("Job Title", width="large"),
                "link": st.column_config.LinkColumn("Link", width="medium"),
                "description": st.column_config.TextColumn("Description", width="large"),
                "source": st.column_config.TextColumn("Platform", width="small"),
                "Type": st.column_config.TextColumn("Type", width="small")
            },
            hide_index=True,
            height=400
        )
        
        download_results(all_results)
        display_platform_stats(all_results)
    else:
        st.warning("No opportunities found. Try different search terms or locations.")
    
    display_search_tips()

def download_results(results):
    csv_buffer = StringIO()
    results.to_csv(csv_buffer, index=False)
    
    st.download_button(
        label="📥 Download Results as CSV",
        data=csv_buffer.getvalue(),
        file_name=f"job_search_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def display_platform_stats(results):
    platform_stats = results.groupby("source").size().reset_index(name="count")
    st.subheader("Results by Platform")
    st.bar_chart(platform_stats.set_index("source"))

def display_search_tips():
    with st.expander("💡 Search Tips"):
        st.markdown("""
        ### Tips for Better Results
        
        - **Be specific** with job titles for more relevant results
        - **Try different locations** to expand your search
        - **Use keywords** related to your skills (e.g., "Python Developer" instead of just "Developer")
        - **Internshala** is specialized for internships in India
        - **LinkedIn and Indeed** typically have the most comprehensive job listings
        """)