import requests
from bs4 import BeautifulSoup
import pandas as pd

# Step 1: Start a session
session = requests.Session()

# Step 2: Get the login page (optional, but might be needed to get some cookies)
response = session.get('https://nojuice.ag')
# You might need to extract and include CSRF token in the login request, if the website uses CSRF protection

# Step 3: Locate the form data and the action endpoint (inspect the webpage)
login_url = 'https://nojuice.ag' # Replace with the actual login endpoint
login_payload = {
    'customerID': 'xpyragt', # Replace with actual form field name and your username
    'Password': 'cooper.777'  # Replace with actual form field name and your password
    # Include other form fields if necessary, such as CSRF token
}

# Step 4: Send a POST request with your login credentials
response = session.post(login_url, data=login_payload)

# Step 5: Check if login was successful
if response.ok:
    print("Login successful")
else:
    print("Login failed")

# Step 6: Now you are logged in, use the session to access other pages
response = session.get('https://nojuice.ag/manager.html?v=1694964557141#!') # Replace with actual URL
soup = BeautifulSoup(response.text, 'html.parser')
# ... (Now you can use Beautiful Soup to parse and navigate the page DOM)
print(soup.prettify())
# Find the table using its data-table attribute
table = soup.find('div', {'data-content': 'table-weekly-figure'})
print(table)
table = soup.find('table', {'class': 'table table-striped base-table base-table'})
print(table)

div = soup.find('div', {'data-content': 'table-weekly-figure'})
table = div.find('table', {'class': 'total-table'})

if table:
    rows = table.find_all('tr')
    
    # Extract header (column names)
    header = [th.get_text().strip() for th in rows[0].find_all('th')]
    
    # Extract data rows
    data = []
    for row in rows[1:]:
        data.append([td.get_text().strip() for td in row.find_all('td')])
    
    # Create a Pandas DataFrame
    df = pd.DataFrame(data, columns=header)
    print(df)
else:
    print("Table not found")
    
    
    
    
from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import time

# Step 1: Start a session
session = requests.Session()

# Step 2: Get the login page (optional, but might be needed to get some cookies)
response = session.get('https://nojuice.ag')
# You might need to extract and include CSRF token in the login request, if the website uses CSRF protection

# Step 3: Locate the form data and the action endpoint (inspect the webpage)
login_url = 'https://nojuice.ag' # Replace with the actual login endpoint
login_payload = {
    'customerID': 'xpyragt', # Replace with actual form field name and your username
    'Password': 'cooper.777'  # Replace with actual form field name and your password
    # Include other form fields if necessary, such as CSRF token
}

# Step 4: Send a POST request with your login credentials
response = session.post(login_url, data=login_payload)

# Step 5: Check if login was successful
if response.ok:
    print("Login successful")
else:
    print("Login failed")

# Step 6: Now you are logged in, use the session to access other pages
response = session.get('https://nojuice.ag/manager.html?v=1694964557141#!') # Replace with actual URL

# Now that we are logged in, initiate Selenium to deal with dynamic content/iframe
driver = webdriver.Chrome()

# Use Selenium to open the page (we're assuming that the cookies set by the requests library will carry over, but this might not be the case)
driver.get('https://nojuice.ag/manager.html?v=1694964557141#!')

# Give some time for page to load and JavaScript to execute
time.sleep(5)

# If the content is inside an iframe, switch to it (replace 'iframe_name_or_id' with actual value)
# driver.switch_to.frame('iframe_name_or_id')

# Get page source and parse with Beautiful Soup
page_source = driver.page_source
soup = BeautifulSoup(page_source, 'html.parser')
print(soup.prettify())
div = soup.find('div', {'data-content': 'table-weekly-figure'})
table = soup.find('table', {'class': 'total-table'})# Use Beautiful Soup to scrape the data
# ... (your Beautiful Soup script here)

# Don't forget to quit the driver at the end
driver.quit()
