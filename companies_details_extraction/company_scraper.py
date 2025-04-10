from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import quote
import time
from concurrent.futures import ThreadPoolExecutor


def get_linkedin_company_links(location, domain, num_companies=10):
    """
    Search for LinkedIn company links based on location and domain
    Args:
        location: Location to search for
        domain: Domain/Industry to search for
        num_companies: Number of companies to retrieve (default: 10)
    Returns:
        List of LinkedIn company URLs
    """
    search_queries = [
        f"site:linkedin.com/company {domain} {location}",
        f"site:linkedin.com/company \"{domain}\" \"{location}\"",
        f"site:linkedin.com/company {domain} company {location}",
        f"site:linkedin.com/company {domain} in {location}"
    ]
    
    company_links = []
    seen_links = set()  # To avoid duplicates
    
    # Headless browser options
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    try:
        driver = webdriver.Chrome(options=chrome_options)

        for search_query in search_queries:
            if len(company_links) >= num_companies:
                break

            search_url = f"https://duckduckgo.com/?q={quote(search_query)}&t=h_&ia=web"
            driver.get(search_url)
            attempt = 0

            def process_element(element):
                href = element.get_attribute('href')
                if href and 'linkedin.com/company/' in href and 'linkedin.com/company/jobs' not in href:
                    if href not in seen_links:
                        seen_links.add(href)
                        company_links.append(href)
                        print(f"Found company link: {href}")

            while len(company_links) < num_companies and attempt < 3:
                time.sleep(1.5)

                for _ in range(3):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)

                elements = driver.find_elements(By.CSS_SELECTOR, 'a[href*="linkedin.com/company/"]:not([href*="jobs"])')
                with ThreadPoolExecutor(max_workers=4) as executor:
                    executor.map(process_element, elements)

                attempt += 1  # DuckDuckGo may not support deep pagination
                if len(elements) == 0:
                    break

        driver.quit()
        return company_links[:num_companies]

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
    # Sample input parameters
    test_location = "Ahmedabad"
    test_domain = "IT Services"
    num_companies = 20

    print(f"\n🔍 Searching for {num_companies} {test_domain} companies in {test_location}...\n")

    start_time = time.time()
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    company_links = get_linkedin_company_links(test_location, test_domain, num_companies)

    end_time = time.time()
    print(f"Finished at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏱️ Total Time: {end_time - start_time:.2f} seconds")

    print(f"\n✅ Found {len(company_links)} companies:\n")

    for link in company_links:
        company_name = extract_company_name_from_url(link)
        print(f"🏢 Company: {company_name}")
        print(f"🔗 URL: {link}\n")
