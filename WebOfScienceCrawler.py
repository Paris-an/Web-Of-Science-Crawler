# @author Paris
# @date 2024/8/22
# selenium = 4.23.1
from time import sleep
import random
import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager

# Get the path of the Chrome driver
driver_path = ChromeDriverManager().install()
print(driver_path)
# Create a service instance for the Chrome browser
service = Service(executable_path=driver_path)

options = Options()
# Set user agent
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0'
options.add_argument(f'user-agent={user_agent}')
# Disable image loading to speed up
options.add_argument('--disable-images')
# Ignore certificate errors
options.add_argument('--ignore-certificate-errors')
# Ignore Bluetooth: bluetooth_adapter_winrt.cc:1075 Getting Default Adapter failed. error
options.add_experimental_option('excludeSwitches', ['enable-automation'])
# Ignore DevTools listening on ws://127.0.0.1... message
options.add_experimental_option('excludeSwitches', ['enable-logging'])
# Change other browser identifiers to prevent anti-scraping
options.add_argument('--disable-blink-features=AutomationControlled')  # Prevent detection of webdriver attribute
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--disable-infobars')

options.add_argument("user-data-dir=C:/Users/User/AppData/Local/Google/Chrome/User Data") #add chrome profile for authentication easiness



#-----------------------------《Parameter Adjustment Area》----------------------------------------#
totalDocumentNumber=114563 # Predefined number of documents to scrape

url="https://www.webofscience.com/wos/woscc/summary/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx/relevance/1" # URL to get data, please copy the URL of the search results page after retrieving the desired data



# Mode settings
mode = "Full Record" # Full record
maxNumber = 1000
downloadBatchNum = (totalDocumentNumber // maxNumber) + 1
startBatchNum = 40  # When interrupted unexpectedly, observe "Downloading records" and restart download; set to 0 to download from 0001-1000
endFlag=False
#-----------------------------《Parameter Adjustment Area》----------------------------------------#

def random_sleep(min_time=2, max_time=5):
    """Sleep for a random period of time"""
    sleep_time = random.uniform(min_time, max_time)
    print(f"Sleeping for {sleep_time:.2f} seconds")
    sleep(sleep_time)
def get_current_mouse_position(driver):
    """Get the current mouse position"""
    return driver.execute_script("return { x: window.scrollX + window.innerWidth / 2, y: window.scrollY + window.innerHeight / 2 };")

def human_like_mouse_move(driver):
    """Simulate human-like mouse movement"""
    action = ActionChains(driver)
    current_position = get_current_mouse_position(driver)
    for _ in range(3):  # Randomly move a few times
        x_offset = random.randint(-100, 100)
        y_offset = random.randint(-100, 100)
        try:
            action.move_by_offset(x_offset, y_offset).perform()
            random_sleep(0.5, 1.5)
        except selenium.common.exceptions.MoveTargetOutOfBoundsException:
            # print(f"Move target out of bounds: x_offset={x_offset}, y_offset={y_offset}")
            pass
            # Handle exceptions, may try to reposition
def human_like_scroll(driver):
    """Simulate human-like scrolling"""
    scroll_height = random.randint(100, 500)
    driver.execute_script(f"window.scrollBy(0, {scroll_height});")
    # print(f"Scrolled down {scroll_height} pixels")
    random_sleep(0.5, 2.0)

# Create WebDriver object using service instance
driver = webdriver.Chrome(service=service, options=options)
# print(type(driver))

# while(True):
try:
    for currentBatch in range(startBatchNum, downloadBatchNum):
        # Refresh each time when exporting different batches
        #driver.get(url+"(overlay:export/ext)")  # Set to export as (Tab Delimited File) TXT format
        #driver.get(url + "(overlay:export/exc)")  # Set to export as EXCEL format
        driver.get(url + "(overlay:export/exbt)")  # Set to export as bibtex format
        sleepTime=random.sample(range(20, 40), 1)
        print("Sleeping for " + str(sleepTime[0]) + " seconds! Waiting for results to refresh!")
        sleep(sleepTime[0])

        human_like_mouse_move(driver)  # Simulate mouse movement
        human_like_scroll(driver)      # Simulate page scrolling

        if currentBatch == startBatchNum:
            # Close some pop-ups, e.g., accept cookies, human verification
            try:
                # Set waiting timeout
                wait = WebDriverWait(driver, 5)  # 5 seconds timeout
                # Wait for an element to become visible and clickable
                element = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
                element.click()
                print("Successfully clicked: Accept all cookies")
            except TimeoutException:
                # If waiting times out, execute this code
                print("Waiting timed out, no need to accept cookies")
            except NoSuchElementException:
                # If the element does not exist, execute this code
                print("Cookie element not found")

            try:
                # Set waiting timeout
                wait = WebDriverWait(driver, 5)  # 5 seconds timeout
                # Wait for an element to become visible and clickable
                element = wait.until(EC.element_to_be_clickable((By.XPATH,"/html/body/div[3]/div[2]/div/mat-dialog-container/app-captcha-details/div/div/div/p")))  # Human verification
                if element is not None:
                    print("Please complete human verification within 60 seconds!!!")
                    sleep(60)  # 60 seconds timeout
            except TimeoutException:
                print("Waiting timed out, no need for or did not perform human verification")
            except NoSuchElementException:
                print("No human verification element found")
        else:
            pass

        startNum = currentBatch * maxNumber + 1
        if currentBatch != downloadBatchNum - 1:
            EndNum = (currentBatch + 1) * maxNumber
        else:
            EndNum = totalDocumentNumber

        labelElements = driver.find_elements(By.XPATH, "//label[@for='radio3-input']")
        labelElements[0].click()
        inputElements_1 = driver.find_elements(By.XPATH, "//input[@type='text']")
        inputElements_1[0].clear()
        inputElements_1[0].send_keys(str(startNum))
        inputElements_2 = driver.find_elements(By.XPATH, "//input[@type='text']")
        inputElements_2[1].clear()
        inputElements_2[1].send_keys(str(EndNum))
        closeButtonElements_1 = driver.find_elements(By.XPATH, "//button[@class='_pendo-close-guide']")
        if len(closeButtonElements_1) > 0:
            closeButtonElements_1[0].click()
        dropdownElements = driver.find_elements(By.XPATH, "//button[@class='dropdown']")
        dropdownElements[0].click()
        closeButtonElements_1 = driver.find_elements(By.XPATH, "//button[@class='_pendo-close-guide']")
        if len(closeButtonElements_1) > 0:
            closeButtonElements_1[0].click()
        fullRecordsElements = driver.find_elements(By.XPATH, "//div[@title='" + mode + "']")  # WOS most easily modified part
        fullRecordsElements[0].click()
        closeButtonElements_1 = driver.find_elements(By.XPATH, "//button[@class='_pendo-close-guide']")
        if len(closeButtonElements_1) > 0:
            closeButtonElements_1[0].click()
        exportElements = driver.find_elements(By.XPATH, "//button[@class='mat-focus-indicator mat-flat-button mat-button-base mat-primary']")
        exportElements[0].click()
        sleep(5)
        captchaElements = driver.find_elements(By.XPATH, "//app-captcha-details[@class='ng-star-inserted']")
        if len(captchaElements) > 0:
            startBatchNum = currentBatch
            print("Please set startBatchNum to " + str(startBatchNum) + " and restart")
            driver.close()
            break
        else:
            try:
                print("Downloading records:" + str(startNum) + "~" + str(EndNum) + "!")
                sleepTime = random.sample(range(20, 30), 1)
                print("Sleeping for " + str(sleepTime[0]) + " seconds! Waiting for download to complete!")
                sleep(sleepTime[0])
                wait = WebDriverWait(driver, 200)
                wait.until(EC.invisibility_of_element((By.XPATH, "//button[@class='mat-focus-indicator mat-flat-button mat-button-base mat-primary']")))
                print("Download complete, preparing to download new files!!!")
            finally:
                pass

        if currentBatch == downloadBatchNum - 1:
            endFlag = True
    if endFlag:
        print("Scraping completed!")
except Exception as e:
    print(f"An exception occurred: {e}")
    input("An error occurred, press Enter to continue...")

finally:
    input("Scraping completed or encountered an exception, browser window will remain. Press Enter to close the browser...")
# Close the browser
driver.quit()
