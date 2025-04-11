from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
import time
import pandas as pd
from typing import List, Dict, Any
import concurrent.futures
import functools
import hashlib
import os
import json
from datetime import datetime, timedelta

# Add a simple cache
CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache')
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

def get_cache_key(func_name, *args):
    """Generate a cache key based on function name and arguments"""
    key = f"{func_name}_{args}"
    return hashlib.md5(key.encode()).hexdigest()

def cache_results(func):
    """Decorator to cache search results for 24 hours"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Generate cache key
        cache_key = get_cache_key(func.__name__, *args)
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
        
        # Check if cache exists and is recent (less than 24 hours old)
        if os.path.exists(cache_file):
            file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
            if file_age < timedelta(hours=24):
                try:
                    with open(cache_file, 'r') as f:
                        return json.load(f)
                except:
                    pass  # If cache read fails, continue with normal execution
        
        # Execute function and cache results
        results = func(*args, **kwargs)
        try:
            with open(cache_file, 'w') as f:
                json.dump(results, f)
        except:
            pass  # If cache write fails, just return results
            
        return results
    return wrapper

def setup_driver():
    """Set up and return a headless Chrome driver with optimized settings"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
    
    # Performance optimizations
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')  # Disable images
    
    return webdriver.Chrome(options=chrome_options)

@cache_results
def search_linkedin_jobs(job_title: str, location: str, is_internship: bool = False, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for jobs/internships on LinkedIn"""
    job_type = "internship" if is_internship else "job"
    search_query = f'site:linkedin.com "{job_type}" "{job_title}" "{location}"'
    search_url = f"https://www.bing.com/search?q={quote(search_query)}"
    
    driver = setup_driver()
    results = []
    
    try:
        driver.get(search_url)
        # Reduced wait time
        time.sleep(1.5)
        
        # Find search results
        search_results = driver.find_elements(By.CSS_SELECTOR, "li.b_algo")
        
        for result in search_results[:limit]:  # Use limit parameter
            try:
                title_element = result.find_element(By.CSS_SELECTOR, "h2 a")
                title = title_element.text
                link = title_element.get_attribute("href")
                
                # Extract description if available
                description = ""
                try:
                    description = result.find_element(By.CSS_SELECTOR, "p").text
                except:
                    pass
                
                if "linkedin.com/jobs" in link:
                    results.append({
                        "title": title,
                        "link": link,
                        "description": description,
                        "source": "LinkedIn"
                    })
            except Exception as e:
                continue
    
    except Exception as e:
        print(f"Error searching LinkedIn jobs: {e}")
    
    finally:
        driver.quit()
    
    return results

# Apply similar optimizations to other search functions
@cache_results
def search_indeed_jobs(job_title: str, location: str, is_internship: bool = False, limit: int = 10) -> List[Dict[str, Any]]:
    """Search for jobs/internships on Indeed"""
    job_type = "internship" if is_internship else "job"
    search_query = f'site:indeed.com "{job_type}" "{job_title}" "{location}"'
    search_url = f"https://www.bing.com/search?q={quote(search_query)}"
    
    # Similar implementation with reduced wait time
    driver = setup_driver()
    results = []
    
    try:
        driver.get(search_url)
        # Reduced wait time
        time.sleep(1.5)
        
        # Find search results
        search_results = driver.find_elements(By.CSS_SELECTOR, "li.b_algo")
        
        for result in search_results[:limit]:  # Use limit parameter
            try:
                title_element = result.find_element(By.CSS_SELECTOR, "h2 a")
                title = title_element.text
                link = title_element.get_attribute("href")
                
                # Extract description if available
                description = ""
                try:
                    description = result.find_element(By.CSS_SELECTOR, "p").text
                except:
                    pass
                
                if "indeed.com" in link:
                    results.append({
                        "title": title,
                        "link": link,
                        "description": description,
                        "source": "Indeed"
                    })
            except Exception as e:
                continue
    
    except Exception as e:
        print(f"Error searching Indeed jobs: {e}")
    
    finally:
        driver.quit()
    
    return results

def search_internshala_jobs(job_title: str, location: str) -> List[Dict[str, Any]]:
    """
    Search for internships on Internshala
    
    Args:
        job_title: Job title or keywords
        location: Location for job search
    
    Returns:
        List of internship listings with details
    """
    search_query = f"{job_title} internship {location} site:internshala.com"
    search_url = f"https://www.bing.com/search?q={quote(search_query)}"
    
    driver = setup_driver()
    results = []
    
    try:
        driver.get(search_url)
        time.sleep(3)
        
        # Find search results
        search_results = driver.find_elements(By.CSS_SELECTOR, "li.b_algo")
        
        for result in search_results[:10]:  # Limit to first 10 results
            try:
                title_element = result.find_element(By.CSS_SELECTOR, "h2 a")
                title = title_element.text
                link = title_element.get_attribute("href")
                
                # Extract description if available
                description = ""
                try:
                    description = result.find_element(By.CSS_SELECTOR, "p").text
                except:
                    pass
                
                if "internshala.com" in link:
                    results.append({
                        "title": title,
                        "link": link,
                        "description": description,
                        "source": "Internshala"
                    })
            except Exception as e:
                print(f"Error processing Internshala result: {e}")
                continue
    
    except Exception as e:
        print(f"Error searching Internshala jobs: {e}")
    
    finally:
        driver.quit()
    
    return results

def search_glassdoor_jobs(job_title: str, location: str, is_internship: bool = False, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search for jobs/internships on Glassdoor
    
    Args:
        job_title: Job title or keywords
        location: Location for job search
        is_internship: Whether to search for internships specifically
    
    Returns:
        List of job listings with details
    """
    job_type = "internship" if is_internship else "job"
    search_query = f"{job_title} {job_type} {location} site:glassdoor.com/job"
    search_url = f"https://www.bing.com/search?q={quote(search_query)}"
    
    driver = setup_driver()
    results = []
    
    try:
        driver.get(search_url)
        time.sleep(3)
        
        # Find search results
        search_results = driver.find_elements(By.CSS_SELECTOR, "li.b_algo")
        
        for result in search_results[:limit]:  # Use limit parameter
            try:
                title_element = result.find_element(By.CSS_SELECTOR, "h2 a")
                title = title_element.text
                link = title_element.get_attribute("href")
                
                # Extract description if available
                description = ""
                try:
                    description = result.find_element(By.CSS_SELECTOR, "p").text
                except:
                    pass
                
                if "glassdoor.com" in link:
                    results.append({
                        "title": title,
                        "link": link,
                        "description": description,
                        "source": "Glassdoor"
                    })
            except Exception as e:
                print(f"Error processing Glassdoor result: {e}")
                continue
    
    except Exception as e:
        print(f"Error searching Glassdoor jobs: {e}")
    
    finally:
        driver.quit()
    
    return results

def search_all_platforms(job_title: str, location: str, is_internship: bool = False, limit: int = 10) -> pd.DataFrame:
    """
    Search for jobs/internships across all supported platforms using parallel processing
    
    Args:
        job_title: Job title or keywords
        location: Location for job search
        is_internship: Whether to search for internships specifically
        limit: Number of results to fetch from each platform
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all search tasks with limit parameter
        linkedin_future = executor.submit(search_linkedin_jobs, job_title, location, is_internship, limit)
        indeed_future = executor.submit(search_indeed_jobs, job_title, location, is_internship, limit)
        glassdoor_future = executor.submit(search_glassdoor_jobs, job_title, location, is_internship, limit)
        
        # Get results as they complete
        all_results = []
        all_results.extend(linkedin_future.result())
        all_results.extend(indeed_future.result())
        all_results.extend(glassdoor_future.result())
        
        # Only search Internshala for internships
        if is_internship:
            internshala_future = executor.submit(search_internshala_jobs, job_title, location)
            all_results.extend(internshala_future.result())
    
    # Convert to DataFrame
    if all_results:
        return pd.DataFrame(all_results)
    else:
        return pd.DataFrame(columns=["title", "link", "description", "source"])

# Test code
if __name__ == "__main__":
    def test_job_search():
        print("Testing job search functionality...")
        
        # Test parameters
        job_title = "software developer"
        location = "Ahmedabad"
        
        # Test job search
        print("\n=== Testing Regular Job Search ===")
        jobs_df = search_all_platforms(job_title, location, is_internship=False)
        print(f"Found {len(jobs_df)} job listings")
        if not jobs_df.empty:
            print(jobs_df[["title", "source"]].head())
        
        # Test internship search
        print("\n=== Testing Internship Search ===")
        internships_df = search_all_platforms(job_title, location, is_internship=True)
        print(f"Found {len(internships_df)} internship listings")
        if not internships_df.empty:
            print(internships_df[["title", "source"]].head())
        
        # Test individual platforms
        print("\n=== Testing LinkedIn Search ===")
        linkedin_results = search_linkedin_jobs(job_title, location, is_internship=False)
        print(f"Found {len(linkedin_results)} LinkedIn job listings")
        
        print("\n=== Testing Internshala Search ===")
        internshala_results = search_internshala_jobs(job_title, location)
        print(f"Found {len(internshala_results)} Internshala listings")
        
        return jobs_df, internships_df
    
    # Run the test
    jobs, internships = test_job_search()