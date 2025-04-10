from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote
import time

def get_linkedin_company_links(location, domain, num_companies=10):
    """
    Search for LinkedIn company links based on location and domain
    Args:
        location: Location to search for
        domain: Domain/Industry to search for
        num_companies: Number of companies to retrieve (default: 10)
    """
    search_query = f"site:linkedin.com/company {domain} {location}"
    search_url = f"https://duckduckgo.com/?q={quote(search_query)}&t=h_&ia=web"
    
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(search_url)
        
        company_links = []
        max_attempts = 5
        attempt = 0
        
        while len(company_links) < num_companies and attempt < max_attempts:
            # Wait for results to load
            time.sleep(3)
            
            # Scroll down to load more results
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Try both selectors
            elements = driver.find_elements(By.CSS_SELECTOR, 'a.result__url')
            if not elements:
                elements = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="result-title-a"]')
            
            for element in elements:
                if len(company_links) >= num_companies:
                    break
                    
                href = element.get_attribute('href')
                if href and 'linkedin.com/company/' in href and 'linkedin.com/company/jobs' not in href:
                    if href not in company_links:
                        company_links.append(href)
                        print(f"Found company link: {href}")
            
            attempt += 1
        
        driver.quit()
        return company_links[:num_companies]  # Return only requested number of companies
    except Exception as e:
        print(f"Error details: {str(e)}")
        if 'driver' in locals():
            driver.quit()
        return []

def extract_company_name_from_url(url):
    """
    Extract company name from LinkedIn company URL
    """
    try:
        company_name = url.split('/company/')[1].split('/')[0]
        return company_name.replace('-', ' ').title()
    except:
        return url


if __name__ == "__main__":
    # Test parameters
    test_location = "Ahmedabad"
    test_domain = "IT Services"
    num_companies = 5  # Specify number of companies to retrieve
    
    print(f"Testing company search for {num_companies} {test_domain} companies in {test_location}")
    
    # Test get_linkedin_company_links with num_companies parameter
    company_links = get_linkedin_company_links(test_location, test_domain, num_companies)
    print(f"\nFound {len(company_links)} companies:")
    
    # Test extract_company_name_from_url for each link
    for link in company_links:
        company_name = extract_company_name_from_url(link)
        print(f"Company: {company_name}")
        print(f"URL: {link}\n")
