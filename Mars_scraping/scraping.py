# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager


def scrape_all():
    # Initiate headless driver for deployment
    # Set up Splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)
  
    # Run all scraping functions and store results in a dictionary

    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": hemisphere_image(browser) 
     }
    
    # Stop webdriver and return data
    browser.quit()
    return data

def mars_news(browser):
    
    # Scrape Mars News
    # Visit the mars nasa news site
    # url = 'https://redplanetscience.com/'
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:
        return None, None

    return news_title, news_p

# ### JPL Space Images Featured Images

def featured_image(browser):
    # Visit URL
    # url = 'https://spaceimages-mars.com'
    url = 'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html'
    import time 

    browser.visit(url)
    time.sleep(3)

    # Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    # img_url = f'https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/{img_url_rel}'

    return img_url

# ## Mars Facts

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
        
        # df = pd.read_html('https://data-class-mars-facts.s3.amazonaws.com/Mars_Facts/index.html')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
        
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    # return df.to_html()
    return df.to_html(classes="table table-striped")

def hemisphere_image(browser):
     # 1. Use browser to visit the URL 
    url = 'https://marshemispheres.com/'
    import time

    browser.visit(url)
    time.sleep(3)

    html = browser.html
    home_soup = soup(html, 'html.parser')

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.

    hemi_thumb_list= home_soup.find_all('img', class_="thumb")

    # Using a for loop, iterate through the tags or CSS element.
    for hemi_thumb in hemi_thumb_list:
        # Create a dictionary to hold each hemisphere image and title 
        hemisphere = {}
        # Find the HTML tag that holds all the links to the full-resolution images, 
        hemi_page_url = hemi_thumb.parent.get('href')
        # get the full image url
        hemi_page_full_url =f'{url}{ hemi_page_url}'
        # navigate to the full-resolution image page, 
        browser.visit(hemi_page_full_url)
        html = browser.html
        hemi_soup = soup(html, 'html.parser')
        # retrieve the full-resolution image URL string and title for the hemisphere image, 
        title = hemi_soup.find('h2', class_='title').text
        img_link = hemi_soup.find('a',text='Sample').get('href')
    
        hemisphere ={
        'img_url': f'{url}{img_link}',
        'title': title
        }
     
        hemisphere_image_urls.append(hemisphere)

    return hemisphere_image_urls

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())

