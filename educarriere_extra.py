import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException
import time
import pandas as pd # Import pandas pour lire le CSV

# Configuration
driver_path = "C:\\Users\\DELL\\OneDrive - ENSEA\\Desktop\\selenium\\chromedriver-win64\\chromedriver.exe"
output_csv_file = "offres_emploi_scraped.csv"  # Nom du fichier de sortie
input_csv_file = "lien3.csv" # Nom du fichier CSV contenant les URLs
url_column_name = "Lien"  # Nom de la colonne contenant les URLs

# Options du navigateur (vous pouvez activer le mode headless si besoin)
options = webdriver.ChromeOptions()
# options.add_argument("--headless=new") # Décommenter pour le mode headless
options.add_argument("--incognito")

def create_csv(fieldnames):
    """Crée un fichier CSV avec les en-têtes."""
    with open(output_csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

def append_to_csv(data):
    """Ajoute les données scrapées au fichier CSV."""
    with open(output_csv_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=data.keys()) # Utilisation de DictWriter pour l'ajout
        writer.writerow(data)

def scrape_job_details(url):
    """Scrape les détails d'une offre à partir d'une URL."""
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        try:
            post_content = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".text-col.post.small-post.col-md-9.col-xs-12")))
        except TimeoutException:
            print(f"Erreur : Délai d'attente dépassé pour l'URL : {url}")
            return None
        except Exception as e:
            print(f"Erreur : La page n'a pas chargé pour l'URL : {url} - Erreur: {e}")
            return None


        def safe_find(selector, method="css", default=""):
            try:
                if method == "css":
                    element = post_content.find_element(By.CSS_SELECTOR, selector)
                elif method == "xpath":
                    element = post_content.find_element(By.XPATH, selector)
                return element.text.strip() if element.text else default # Gérer les éléments vides
            except NoSuchElementException:
                return default

        job_data = {} # Utilisation d'un dictionnaire pour stocker les données
        job_data["Titre"] = driver.find_element(By.CSS_SELECTOR, "h2").text.strip()
        job_data["Métier(s)"] = safe_find("li:nth-child(1)", "css").replace("Métier(s):", "").strip()
        job_data["Niveau(x)"] = safe_find("li:nth-child(2)", "css").replace("Niveau(x):", "").strip()
        job_data["Expérience"] = safe_find("li:nth-child(3)", "css").replace("Expérience:", "").strip()
        job_data["Lieu"] = safe_find("li:nth-child(4)", "css").replace("Lieu:", "").strip()
        job_data["Date de publication"] = safe_find("li:nth-child(5) span", "css")
        job_data["Date limite"] = safe_find("li:nth-child(6) span", "css")

        return job_data

    except Exception as e:
        print(f"Erreur générale lors de l'extraction pour l'URL {url} : {e}")
        return None
    finally:
        driver.quit()

def scrape_jobs_from_csv():
    """Scrape les détails des offres à partir des URLs dans le fichier CSV."""
    print("Début de l'extraction des offres...")

    try:
        df = pd.read_csv(input_csv_file, encoding='utf-8') # Lecture avec pandas pour gérer l'encodage
    except FileNotFoundError:
        print(f"Erreur: Fichier {input_csv_file} non trouvé.")
        return
    except pd.errors.ParserError:
        print(f"Erreur: Impossible de lire le fichier {input_csv_file}. Vérifiez son format.")
        return


    urls = df[url_column_name].tolist() # Récupération des URLs dans une liste

    if urls:
        create_csv(list(scrape_job_details(urls[0]).keys())) # Création du CSV avec les bons headers
        for url in urls:
            print(f"Scraping : {url}")
            scraped_data = scrape_job_details(url)
            if scraped_data:
                append_to_csv(scraped_data)
            time.sleep(1)  # Délai pour éviter d'être bloqué
        print(f"Extraction terminée. Les données ont été sauvegardées dans {output_csv_file}.")
    else:
        print("Aucune URL trouvée dans le fichier CSV.")

if __name__ == "__main__":
    scrape_jobs_from_csv()