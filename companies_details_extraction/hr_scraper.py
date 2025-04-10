from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote
import time

def get_hr_profiles(company_name, num_profiles, designation="HR OR Recruiter"):
    # Use the designation parameter in the search query
    search_query = f'site:linkedin.com/in "{company_name}" ({designation})'
    search_url = f"https://www.bing.com/search?q={quote(search_query)}"
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    profile_links = []
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(search_url)
        print(f"Searching URL: {search_url}")
        
        time.sleep(3)  # Let page fully load

        # Bing selector for search result links
        results = driver.find_elements(By.CSS_SELECTOR, 'li.b_algo h2 a')
        print(f"Found {len(results)} search results.")

        for result in results:
            href = result.get_attribute("href")
            if href and "linkedin.com/in/" in href and href not in profile_links:
                profile_links.append(href)
                print(f"✔️ Found LinkedIn profile: {href}")
                if len(profile_links) >= num_profiles:
                    break

        driver.quit()
        return profile_links

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return []

def batch_process_companies(companies_list, num_profiles, designation="HR OR Recruiter"):
    """Process multiple companies and return their profiles"""
    all_results = {}
    for company in companies_list:
        profiles = get_hr_profiles(company, num_profiles, designation)
        all_results[company] = profiles
    return all_results

# Optional test run
if __name__ == "__main__":
    test_company = "Sapphire Software Solutions"
    links = get_hr_profiles(test_company, num_profiles=5)
    print("\nLinkedIn HR Profiles:")
    for link in links:
        print(link)
