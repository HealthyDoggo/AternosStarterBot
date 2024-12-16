import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import threading
def startingServer(starting):
  start = time.perf_counter()
#   driver = uc.Chrome(driver_executable_path=r'usr\bin\chromedriver', headless=True)
  driver = uc.Chrome()
  driver.get('https://aternos.org/go')
  driver.find_element(By.XPATH, "//input[@placeholder='Username']").send_keys('StarterBot')
  driver.find_element(By.XPATH, "//input[@placeholder='••••••••']").send_keys('BotAccount')
  driver.find_element(By.XPATH, "//button[@title='Login']").click()
  time.sleep(2)
  try:
    driver.find_element(By.XPATH, '//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]').click()
  except: pass
  WebDriverWait(driver, 10).until(EC.element_to_be_clickable(driver.find_element(By.XPATH, "//div[normalize-space()='roadblocksjailbrokey']"))).click()
  try:
    WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.XPATH, '//*[@id="zoasZkFpIrVS"]/div/div/div[3]/div[2]/div[1]'))).click()
    time.sleep(3)
  except TimeoutException:
    pass
  driver.get('https://aternos.org/server/#goog_rewarded')
  try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="theme-switch"]/div[8]/div[2]/div[1]/div[2]/div[2]/button[1]'))).click()
  except: pass
  time.sleep(1)
  driver.refresh()
  elements = driver.find_elements(By.XPATH, "//div[@id='start']")
  ifClickable = True
  try:
     WebDriverWait(driver, 1).until(EC.element_to_be_clickable(elements[0]))
  except TimeoutException:
     ifClickable = False
  if elements and ifClickable:
      if starting == False:
         return True
      print(elements)
      elements[0].click()
      time.sleep(2)
  else:
      return False
  elements = driver.find_elements(By.XPATH, "//*[contains(., 'Start')]")
  if elements:
     elements[0].click()
  elements = driver.find_elements(By.XPATH, '//*[@id="theme-switch"]/dialog/main/div[2]/button')
  if elements:
      elements[0].click()
  elements = driver.find_elements(By.XPATH, "//*[contains(., 'No')]")
  if elements:
      elements[0].click()
  WebDriverWait(driver, 1000).until(EC.text_to_be_present_in_element((By.CLASS_NAME, "statuslabel-label"), "Online"))
  end = time.perf_counter()
  time.sleep(0.5)
  driver.quit()
  return end-start
def get_player_names():
        consented = False
        driver = uc.Chrome()
        driver.get('https://aternos.org/go')
        driver.find_element(By.XPATH, "//input[@placeholder='Username']").send_keys('StarterBot')
        driver.find_element(By.XPATH, "//input[@placeholder='••••••••']").send_keys('BotAccount')
        driver.find_element(By.XPATH, "//button[@title='Login']").click()
        time.sleep(2)
        try:
          WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="qc-cmp2-ui"]/div[2]/div/button[2]'))).click()
        except: pass
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable(driver.find_element(By.XPATH, "//div[normalize-space()='roadblocksjailbrokey']"))).click()
        try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="zoasZkFpIrVS"]/div/div/div[3]/div[2]/div[1]'))).click()
            time.sleep(3)
        except:
            pass
        time.sleep(0.5)
        driver.get('https://aternos.org/server/#goog_rewarded')
        try:
          WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="theme-switch"]/div[8]/div[2]/div[1]/div[2]/div[2]/button[1]'))).click()
          consented = True
        except: pass
        driver.refresh()
        time.sleep(0.5)
        driver.find_element(By.XPATH, "//a[@title='Players']").click()
   # Wait for the online player cards to appear
        # Wait for the specific div containing the online player cards to appear
        if consented == False:
          try:
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="theme-switch"]/div[8]/div[2]/div[1]/div[2]/div[2]/button[1]'))).click()
          except: pass           
        online_player_div = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'playercardlist.online.collapsed'))  # Adjust with the actual ID
)

# Find the online player cards within the specific div
        online_player_cards = online_player_div.find_elements(By.CLASS_NAME, "playercard.has-details")
        online_player_names = [card.get_attribute("data-playername") for card in online_player_cards if card.get_attribute("data-playername")]
        print(online_player_names)
        time.sleep(0.5)
        driver.quit()
        return online_player_names
if __name__ == '__main__':
    print(get_player_names())

