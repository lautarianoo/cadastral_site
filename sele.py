from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException

DIRECTIONS_LIGHT = {"north": [0, 7], "south": [0, -7], "east": [-7, 0], "west": [7, 0], "northeast": [-7, 7], "southeastern": [-7, -7], "southwest": [7, -7], "northwest": [7, 7]}

def parsing_cadastral(cadastral_num):

    data = {"objects": []}

    service = Service()
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('headless')
    options.add_argument('--no-sandbox')
    browser = webdriver.Chrome(service=service, options=options)
    stealth(driver=browser,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/83.0.4103.53 Safari/537.36',
            languages=["ru-RU", "ru"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            run_on_insecure_origins=True,
            )
    browser.get('https://pkk.rosreestr.ru/#/search/65.6495169999989,122.73014399999789/4/@5w3tqw5ca')
    browser.set_window_size(1000, 1000)
    time.sleep(3)
    #Пропустить обучение
    training_button = browser.find_element(By.CLASS_NAME, "tutorial-button-outline")
    training_button.click()
    time.sleep(1.5)
    #Закрытие окна подробностей
    window_more = browser.find_element(By.CLASS_NAME, "close-icon-container")
    window_more.click()

    #Взятие данных у принимаемого номера
    input_cadastral = browser.find_element(By.CLASS_NAME, "type-ahead-select")
    input_cadastral.send_keys(cadastral_num + Keys.RETURN)
    time.sleep(2.5)
    data["main_object"] = {"address": browser.find_element(By.CLASS_NAME, "title-description").text, "cadastral_num": cadastral_num,
                           "square": browser.find_elements(By.CLASS_NAME, "expanding-box_content")[5].text}

    #Перенаправление мышки на центр main_object
    map = browser.find_element(By.ID, "map-area")
    x_center = 715
    y_center =  440
    ActionChains(browser).move_by_offset(x_center, y_center).click().perform()
    time.sleep(3)

    #Увеличение карты до 1 км (6 раз)
    for i in range(6):
        plus_button = browser.find_elements(By.CLASS_NAME, "zoom-button")
        plus_button[2].click()

    #Клики по направления света
    for key, value in DIRECTIONS_LIGHT.items():
        active_x = 715
        active_y = 440
        for m in range(7):
            time.sleep(3)
            active_x -= value[0]
            active_y -= value[1]
            ActionChains(browser).reset_actions()
            ActionChains(browser).move_by_offset(active_x, active_y).click().perform()
            time.sleep(4)
            items = browser.find_elements(By.CLASS_NAME, "info-item-container")
            if len(items) == 1:
                #if browser.find_elements(By.CLASS_NAME, "expanding-box_content")[1].text == "Земельный участок":
                data["objects"].append(
                        {"direction": key, "address": browser.find_element(By.CLASS_NAME, "title-description").text,
                         "square": browser.find_elements(By.CLASS_NAME, "expanding-box_content")[5].text,
                         "cadastral_num": browser.find_element(By.CLASS_NAME, "number").text})
            else:
                i = 0
                for item in items:
                    i +=1
                    try:
                        item.click()
                    except (ElementNotInteractableException, ElementClickInterceptedException):
                        continue
                    time.sleep(3)
                    try:
                        #if browser.find_elements(By.CLASS_NAME, "expanding-box_content")[1].text == "Земельный участок":
                        data["objects"].append({"direction": key, "address": browser.find_element(By.CLASS_NAME, "title-description").text,
                                            "square": browser.find_elements(By.CLASS_NAME, "expanding-box_content")[5].text, "cadastral_num": browser.find_element(By.CLASS_NAME, "number").text})
                        time.sleep(3)
                        browser.execute_script("window.history.go(-1)")
                    except (NoSuchElementException, ElementNotInteractableException):
                        browser.execute_script("window.history.go(-1)")
                    time.sleep(1)
                    if i == 10:
                        browser.execute_script("arguments[0].scrollIntoView();", items[-1])

        ActionChains(browser).reset_actions()
        return_cadastral = browser.find_element(By.CLASS_NAME, "type-ahead-select")
        return_cadastral.click()
        return_cadastral.clear()
        return_cadastral.send_keys(cadastral_num + Keys.RETURN)
        time.sleep(4)

        ActionChains(browser).move_by_offset(x_center, y_center).click().perform()
        time.sleep(4)

        for l in range(6):
            plus_button = browser.find_elements(By.CLASS_NAME, "zoom-button")
            plus_button[2].click()

        print(data)
    browser.quit()
    return data

if __name__ == "__main__":
    parsing_cadastral("36:34:0206001:22471")