# Fixes to get Selenium to work
When chromedriver gets outdated just download and install correct version from:  
https://googlechromelabs.github.io/chrome-for-testing/  

Make sure to copy the driver to the actual place used in application. For example ```/usr/bin/chromedriver``` 

```
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install ./google-chrome-stable_current_amd64.deb
google-chrome-stable --no-sandbox
```

```
wget https://storage.googleapis.com/chrome-for-testing-public/<VERSION>/linux64/chromedriver-linux64.zip
unzip chromedriver-linux64.zip
cd chromedriver-linux64
cp chromedriver /usr/bin/chromedriver
```

## Additional settings
```
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-notifications')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome('/usr/bin/chromedriver', chrome_options=chrome_options)
driver.get(URL)
```