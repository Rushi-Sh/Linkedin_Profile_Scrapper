from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote
import time

def process_result(result, profile_links):
    href = result.get_attribute("href")
    if href and "linkedin.com/in/" in href and href not in profile_links:
        profile_links.append(href)
        print(f"✔️ Found LinkedIn profile: {href}")

def get_hr_profiles(company_name, num_profiles, designation="HR OR Recruiter", country="India", state="Gujarat"):
    """
    Search for HR profiles on LinkedIn
    Args:
        company_name: Name of the company to search for
        num_profiles: Number of profiles to retrieve
        designation: Job title to search for (default: "HR OR Recruiter")
        country: Country to filter by (optional)
        state: State/region to filter by (optional)
    """
    location_filter = ""
    if country and state:
        location_filter = f" AND ({country} AND {state})"
    elif country:
        location_filter = f" AND {country}"
    elif state:
        location_filter = f" AND {state}"
        
    search_query = f'site:linkedin.com/in "{company_name}" ({designation}){location_filter}'
    search_url = f"https://www.bing.com/search?q={quote(search_query)}&first=1"
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    profile_links = []
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        
        while len(profile_links) < num_profiles:
            driver.get(search_url)
            print(f"🔍 Searching: {search_url}")
            
            time.sleep(2)

            results = driver.find_elements(By.CSS_SELECTOR, 'li.b_algo h2 a')
            print(f"🔗 Total search results found: {len(results)}")

            for result in results:
                if len(profile_links) >= num_profiles:
                    break
                process_result(result, profile_links)
            
            # Check if we need more results and can paginate
            if len(profile_links) < num_profiles:
                try:
                    next_page = driver.find_element(By.CSS_SELECTOR, 'a.sb_pagN')
                    search_url = next_page.get_attribute('href')
                except:
                    print("⚠️ No more pages available")
                    break

        driver.quit()
        return profile_links

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return []

def batch_process_companies(companies_list, num_profiles, designation="HR OR Recruiter", country=None, state=None):
    """Process multiple companies and get HR profile links"""
    all_results = {}
    
    for company in companies_list:
        print(f"\n📦 Processing company: {company}")
        all_results[company] = get_hr_profiles(company, num_profiles, designation, country, state)
    
    return all_results

# Optional test run
if __name__ == "__main__":
    import time

    start_time = time.time()

    test_company = "Sapphire Software Solutions"
    links = get_hr_profiles(test_company, num_profiles=20)

    end_time = time.time()
    duration = end_time - start_time

    print("\n📄 LinkedIn HR Profiles:")
    for link in links:
        print(link)

    print(f"\n⏱️ Total Execution Time: {duration:.2f} seconds")
