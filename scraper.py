import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

def scrape_course_content(url):
    print(f"Scraping course content from {url}")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract relevant content - this will need customization
    content = []
    for section in soup.find_all('div', class_='section'):
        title = section.find('h2').text if section.find('h2') else "Untitled"
        text = section.get_text(separator='\n', strip=True)
        content.append({'title': title, 'text': text})
    
    return pd.DataFrame(content)

def scrape_discourse_posts(base_url, start_date, end_date):
    print(f"Scraping Discourse posts from {base_url} between {start_date} and {end_date}")
    # This is a simplified version - real implementation would paginate
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    posts = []
    for topic in soup.find_all('tr', class_='topic-list-item'):
        date_str = topic.find('time')['datetime']
        # Add date filtering logic here
        title = topic.find('a', class_='title').text.strip()
        url = base_url + topic.find('a', class_='title')['href']
        posts.append({'title': title, 'url': url, 'date': date_str})
    
    return pd.DataFrame(posts)

if __name__ == '__main__':
    course_url = "https://tds.s-anand.net/#/2025-01/"
    discourse_url = "https://discourse.onlinedegree.iitm.ac.in/c/courses/tds-kb/34"
    
    course_df = scrape_course_content(course_url)
    posts_df = scrape_discourse_posts(discourse_url, "2025-01-01", "2025-04-15")
    
    # Save the data
    course_df.to_csv('course_content.csv', index=False)
    posts_df.to_csv('discourse_posts.csv', index=False)