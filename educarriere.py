import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time

# Chemin vers le driver Selenium (à adapter)
driver_path = "C:\\Users\\DELL\\OneDrive - ENSEA\\Desktop\\selenium\\chromedriver-win64\\chromedriver.exe"
# Nom du fichier CSV
csv_file = "offres_emploi_educa.csv"

def create_csv():
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Titre", "Métier(s)"]) # En-têtes CSV adaptés

def append_to_csv(data):
    with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(data)

def safe_find(element, selector, method="css", default=""): # element en argument
    try:
        if method == "css":
            return element.find_element(By.CSS_SELECTOR, selector).text.strip()
        elif method == "xpath":
            return element.find_element(By.XPATH, selector).text.strip()
        else:
            return default  # Gérer les autres méthodes si besoin
    except NoSuchElementException:
        return default

def scrape_job_details(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--headless=new") # Mode headless
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        try:
            post_content = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".text-col.post.small-post.col-md-9.col-xs-12")
            ))
        except TimeoutException:
            print(f"Erreur : La page n'a pas chargé pour l'URL : {url}")
            return None

        try:
            title_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h4.post-title a")))
            job_title = title_element.text.strip()
        except (TimeoutException, NoSuchElementException):
            print(f"Titre non trouvé pour : {url}")
            job_title = "Titre non trouvé"

        metiers = safe_find(post_content, "li:nth-child(1)", "css") # Correction ici
        job_data = (job_title, metiers)
        return job_data

    except Exception as e:
        print(f"Erreur inattendue pour {url}: {e}")
        return None
    finally:
        driver.quit()

def scrape_jobs_to_csv(start_id, end_id):
    print("Début de l'extraction...")
    create_csv()
    for page_id in range(start_id, end_id + 1):
        url = f"https://emploi.educarriere.ci/emploi/page/emploi/{page_id}"
        print(f"Scraping : {url}")
        data = scrape_job_details(url)
        if data:
            append_to_csv(data)
        time.sleep(1)
    print(f"Extraction terminée. Données sauvegardées dans {csv_file}.")

if __name__ == "__main__":
    START_ID = 1
    END_ID = 26
    scrape_jobs_to_csv(START_ID, END_ID)