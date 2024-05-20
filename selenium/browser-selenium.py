from selenium import webdriver
from selenium.webdriver.chrome.options import Options


def open_browser_in_incognito_mode(url):
    chrome_options = Options()
    chrome_options.add_argument("--incognito")

    # Replace 'chromedriver_path' with the path to your Chrome WebDriver executable.
    driver = webdriver.Chrome(executable_path='/usr/lib/chromium-browser/chromedriver', options=chrome_options)

    driver.get(url)

    # You can now interact with the web page using Selenium methods.
    # For example, let's print the page title:
    print("Page Title:", driver.title)

    # Perform additional interactions as needed.

    # Don't forget to close the browser when you're done.
    driver.quit()


if __name__ == "__main__":
    # Specify the URL you want to open in incognito mode.
    url = "https://example.com"
    open_browser_in_incognito_mode(url)
