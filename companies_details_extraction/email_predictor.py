import re
from typing import List, Dict
import pandas as pd
from urllib.parse import urlparse


def extract_name_from_linkedin_url(url: str) -> str:
    """Extract name from LinkedIn profile URL"""
    try:
        path = urlparse(url).path
        name_part = path.split('/in/')[1].split('/')[0]
        return ' '.join([part.capitalize() for part in name_part.split('-')])
    except:
        return ""


def predict_email_formats(name: str, domain: str) -> List[str]:
    """
    Predict possible email formats based on name and company domain
    Returns list of possible email formats
    """
    if not name or not domain:
        return []
    
    first_name, *last_name_parts = name.split()
    last_name = ' '.join(last_name_parts) if last_name_parts else ""
    
    formats = []
    
    # Common email formats
    if first_name and last_name:
        formats.extend([
            f"{first_name[0]}{last_name}@{domain}",  # jsmith@domain.com
            f"{first_name}.{last_name}@{domain}",    # john.smith@domain.com
            f"{first_name}_{last_name}@{domain}",   # john_smith@domain.com
            f"{first_name}{last_name[0]}@{domain}",  # johns@domain.com
            f"{first_name}@{domain}",               # john@domain.com
            f"{first_name[0]}.{last_name}@{domain}",# j.smith@domain.com
        ])
    
    return formats


def predict_emails_from_profiles(profile_urls: List[str], company_domain: str) -> pd.DataFrame:
    """
    Predict email formats for multiple LinkedIn profiles
    Returns DataFrame with profile URLs and predicted email formats
    """
    results = []
    
    for url in profile_urls:
        name = extract_name_from_linkedin_url(url)
        if not name:
            continue
            
        emails = predict_email_formats(name, company_domain)
        for email in emails:
            results.append({
                'Profile URL': url,
                'Name': name,
                'Predicted Email': email,
                'Company Domain': company_domain
            })
    
    return pd.DataFrame(results)


def extract_company_domain(company_url: str) -> str:
    """Extract company domain from LinkedIn company URL"""
    try:
        company_name = company_url.split('/company/')[1].split('/')[0]
        return f"{company_name}.com"
    except:
        return ""