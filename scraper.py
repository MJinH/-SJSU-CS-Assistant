from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from class_config import class_list
from instructor_data import data_list
import os
import sys
import time

load_dotenv()

def init_config(url):
  sys.stdout.reconfigure(encoding='utf-8')
  options = webdriver.ChromeOptions()
  options.add_argument('--headless')  # 브라우저 창 숨기기
  driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
  time.sleep(1)
  driver.get(url)
  time.sleep(3)
  execute_script(driver)
  
  return driver


def execute_script(driver):
  driver.execute_script("""
    const overlays = document.querySelectorAll('.ReactModal__Overlay');
    overlays.forEach(overlay => overlay.style.display = 'none');
  """)
  return


def load_department(driver):
  try:
    # select computer science department
    search_box = driver.find_element(By.CSS_SELECTOR, class_list['searchBox'])
    search_box.click()
    computer_science_option = WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.XPATH, '//div[contains(@class, "css-l0mlil-option") and text()="Computer Science"]'))
    )
    
    driver.execute_script("arguments[0].scrollIntoView(true);", computer_science_option)
    driver.execute_script("arguments[0].click();", computer_science_option)
    time.sleep(2)
    while True:
        # load all instructions
        try:
          show_more_button = driver.find_element(By.XPATH, '//button[contains(text(), "Show More")]')
          driver.execute_script("arguments[0].click();", show_more_button)
          time.sleep(2)
        except Exception as e:
            print(f'Error clicking button: {e}')
            break
  except Exception as e:
    print(f'Erro selecting department: {e}')
    
  return


def load_review(driver):

  while True:
      # load all instructions
      try:
        show_more_button = driver.find_element(By.XPATH, '//button[contains(text(), "Load More Ratings")]')
        driver.execute_script("arguments[0].click();", show_more_button)
        time.sleep(2)
      except Exception as e:
          print(f'Error clicking button: {e}')
          break

  return

def get_department(driver):
  
  load_department(driver)
  html = driver.page_source
  soup = BeautifulSoup(html, 'html.parser')
  a_tags = soup.find_all('a', class_=[class_list['aTag_f'], class_list['aTag_s']])
  prof_data = []
  
  for a_tag in a_tags:
    href = a_tag['href']
    name = a_tag.select_one(class_list['name']).text.strip()
    quality = a_tag.select_one(class_list['quality']).text.strip()
    take_again = a_tag.select(class_list['take_again'])[0].text.strip()
    difficulty = a_tag.select(class_list['difficulty'])[1].text.strip()

    data = {
      'name': name,
      'href': href,
      'quality': quality,
      'take_again': take_again,
      'difficulty': difficulty
    }
    prof_data.append(data)
    
  return prof_data
  
  
def get_review(prof_data, driver):
  review_data = {}
  for data in prof_data:
    href = data['href']
    name = data['name']
    review_data[name] = []
    rate_url = os.getenv('RATE_URL')
    driver.get(rate_url + href)
    
    execute_script(driver)
    load_review(driver)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div_tags = soup.find_all('div', class_=[class_list['comment_f'], class_list['comment_s']])
    
    for i, div_tag in enumerate(div_tags):
      review_data[name].append(div_tag.text.strip())

  return review_data


driver = init_config(os.getenv("URL"))
instructor_data = get_department(driver)
review_data = get_review(data_list, driver)

# print(instructor_data)
# print(review_data)