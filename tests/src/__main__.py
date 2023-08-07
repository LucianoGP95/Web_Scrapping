from selenium import webdriver
from selenium.webdriver.common.by import By

chromedriver_path = ""  # Add the path to your ChromeDriver executable
url = 'https://www.kemono.party/patreon/user/17842329'

def main(chromedriver_path, url):
    driver = webdriver.Chrome(chromedriver_path)
    driver.get(url)
    try:
        image_elements = driver.find_elements(By.XPATH, "//article[@class='post-card']//a[@class='image-link']//img")  # Adjust the XPath to target <img> elements
        for image_element in image_elements:
            image_url = image_element.get_attribute('src')
            print("Image URL:", image_url)
    except Exception as e:
        print("An error occurred:", e)
    driver.close()

if __name__ == '__main__':
    main(chromedriver_path, url)