from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import csv
import time

# Configuration du driver Selenium
driver_path = "C:\\Users\\DELL\\OneDrive - ENSEA\\Desktop\\selenium\\chromedriver-win64\\chromedriver.exe"

def scrape_job_details(url):
    """Extrait les détails d'une offre d'emploi à partir de l'URL donnée."""
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--headless=new")  # Mode sans interface graphique
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        # Attendre que la page charge complètement
        try:
            content_inner = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "content-inner-1")))
        except TimeoutException:
            print(f"Erreur : La page n'a pas chargé pour l'URL : {url}")
            return None

        job_data = {}

        # Fonction pour extraire des éléments de manière sécurisée
        def safe_find(selector, method="css", default=""):
            try:
                if method == "css":
                    return content_inner.find_element(By.CSS_SELECTOR, selector).text.strip()
                elif method == "xpath":
                    return content_inner.find_element(By.XPATH, selector).text.strip()
            except NoSuchElementException:
                return default

        # Extraction des données principales
        job_data["Titre"] = safe_find("h3.title-head a")
        job_data["Date de clôture"] = safe_find("//li[strong[contains(text(),'Date de clôture:')]]", method="xpath")
        job_data["Lieu de travail"] = safe_find("//li[strong[contains(text(),'Lieu de travail')]]/span", method="xpath")
        job_data["Sexe"] = safe_find("//li[strong[contains(text(),'Sexe')]]/span", method="xpath")
        job_data["Niveau"] = safe_find("//li[strong[contains(text(),\"Niveau d'études\")]]/span", method="xpath")


        # Extraire toutes les descriptions listées dans .job-info-box
        try:
            description_elements = content_inner.find_elements(By.CSS_SELECTOR, ".job-info-box p")
            descriptions = [p.text.strip() for p in description_elements if p.text.strip()]
            job_data["Description"] = "\n".join(descriptions)  # Combiner les descriptions avec des sauts de ligne
        except NoSuchElementException:
            job_data["Description"] = "Aucune description trouvée"

        return job_data

    except Exception as e:
        print(f"Erreur inattendue lors de l'extraction pour l'URL {url}: {e}")
        return None

    finally:
        driver.quit()


# Extraction pour une plage d'URLs
def extract_jobs(start_range, end_range, output_file="job_details_ok.csv"):
    print("Début de l'extraction des offres...")
    job_details = []

    for job_number in range(start_range, end_range + 1):
        url = f"https://www.agenceemploijeunes.ci/site/offres-emplois/{job_number}"
        print(f"Scraping : {url}")
        scraped_data = scrape_job_details(url)
        if scraped_data:
            job_details.append(scraped_data)
        time.sleep(1)  # Délai pour éviter d'être bloqué

    print("Extraction terminée. Sauvegarde des données...")

    # Sauvegarde des données dans un fichier CSV
    if job_details:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ["Titre", "Date de clôture", "Lieu de travail", "Sexe","Niveau","Description"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(job_details)
        print(f"Données sauvegardées dans {output_file}")
    else:
        print("Aucune donnée n'a été extraite.")

# Appel principal
if __name__ == "__main__":
    # Définir la plage d'URLs à scraper
    START_RANGE = 40439
    END_RANGE = 40442
    OUTPUT_FILE = "job_details_ok.csv"

    extract_jobs(START_RANGE, END_RANGE, OUTPUT_FILE)
