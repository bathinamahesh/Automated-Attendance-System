from selenium.webdriver.common.selenium_manager import SeleniumManager
from selenium import webdriver
from selenium.webdriver.common.by import By
#cpath = SeleniumManager.driver_location("chrome")
# print(cpath)
driver = webdriver.Chrome()
driver.implicitly_wait(10)
driver.get("https://rguktn.ac.in/examcell/ConsolidatedResults/2018_Engg/")
x = driver.find_element(By.ID, "id")
x.send_keys("N180255")
y = driver.find_element(By.ID, "password")
y.send_keys("12-02-2002")
z = driver.find_element(By.XPATH,
                        "/html/body/section/form/ul/li[3]/input")
z.click()
cgpa = driver.find_element(By.XPATH,
                           "/html/body/div[1]/div/section/div/div/table/thead/tr[3]/th[3]").text


print(cgpa)
driver.close()
