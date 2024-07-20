from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import json

def init_driver() -> webdriver.Chrome:
    service = webdriver.ChromeService(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def get_project_data(driver, target_button, close_button):
    target_button.click()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'project-menu-html')))
    WebDriverWait(driver, 10).until(EC.visibility_of_any_elements_located((By.XPATH, "//tr[td[text()='PAN No.']]/td[2]/span")))

    parent = driver.find_element(By.ID, 'project-menu-html')
    details = {
        'gstin_no': parent.find_element(By.XPATH, "//tr[td[text()='GSTIN No.']]/td[2]/span").text,
        'pan_no': parent.find_element(By.XPATH, "//tr[td[text()='PAN No.']]/td[2]/span").text,
        'name': parent.find_element(By.XPATH, "//tr[td[text()='Name']]/td[2]").text,
        'address': parent.find_element(By.XPATH, "//tr[td[text()='Permanent Address']]/td[2]/span").text
    }

    close_button.click()
    WebDriverWait(driver, 10).until(EC.invisibility_of_element((By.ID, 'project-menu-html')))
    return details


def scrape_projects(limit = None):
    print("Initializing...")
    driver = init_driver()

    url = 'https://hprera.nic.in/PublicDashboard'
    print(f"requesting url: {url}")
    driver.get(url)

    print("waiting for data to load...")
    WebDriverWait(driver, 60).until(EC.visibility_of_element_located((By.ID, 'reg-Projects')))

    projects = []
    project_detail_buttons = driver.find_elements(By.CSS_SELECTOR, 'a[title="View Application"]')
    modal_close_button = driver.find_element(By.XPATH, '//div[@id="modal-data-display-tab_project_main"]/div/div/div[1]/button')

    print(f"found {len(project_detail_buttons)} projects")
    if limit is None:
        limit = len(project_detail_buttons)

    print(f"retrieving {limit} projects...")
    for i in range(limit):
        button = project_detail_buttons[i]
        print(f"fetching project: Ref No({button.text})")
        projects.append(get_project_data(driver, button, modal_close_button))

    driver.quit()
    return projects

if __name__ == "__main__":
    projects = scrape_projects(limit=6)
    print("Saving output to data.json")
    with open("data.json", "w") as f:
        json.dump(projects, f, ensure_ascii=False, indent=4)
    