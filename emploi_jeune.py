import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Chemin vers le driver Selenium
driver_path = "C:\\Users\\DELL\\OneDrive - ENSEA\\Desktop\\selenium\\chromedriver-win64\\chromedriver.exe"

# Nom du fichier CSV
csv_file = "offres_emploi.csv"

# Création du fichier CSV avec en-têtes
def create_csv():
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Titre", "Métier(s)", "Niveau(x)", "Expérience", "Lieu", "Date de publication", "Date limite", "URL"])

# Ajout des données dans le fichier CSV
def append_to_csv(data):
    with open(csv_file, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(data)

# Fonction pour extraire les URLs depuis la page principale
def get_job_urls(home_url):
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--headless=new")  # Mode sans interface graphique
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(home_url)
        wait = WebDriverWait(driver, 10)

        # Attendre que les offres soient chargées
        job_elements = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div.job-post > a")  # Ajustez le sélecteur selon le site
        ))

        # Collecter les URLs des offres
        job_urls = [job.get_attribute("href") for job in job_elements]
        return job_urls

    except Exception as e:
        print(f"Erreur lors de la récupération des URLs : {e}")
        return []

    finally:
        driver.quit()

# Fonction pour scraper les détails d'une offre
def scrape_job_details(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--headless=new")  # Mode sans interface graphique
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)

        # Vérifier si la page contient les détails de l'offre
        try:
            post_content = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".text-col.post.small-post.col-md-9.col-xs-12")
            ))
        except Exception as e:
            print(f"Erreur : La page n'a pas chargé pour l'URL : {url}")
            return None

        # Fonction pour extraire du texte en toute sécurité
        def safe_find(selector, method="css", default=""):
            try:
                if method == "css":
                    return post_content.find_element(By.CSS_SELECTOR, selector).text.strip()
                elif method == "xpath":
                    return post_content.find_element(By.XPATH, selector).text.strip()
            except Exception:
                return default

        # Extraction des données
        job_title = driver.find_element(By.CSS_SELECTOR, "h1").text.strip()  # Titre de l'offre
        metiers = safe_find("li:nth-child(1)", "css").replace("Métier(s):", "").strip()
        niveau = safe_find("li:nth-child(2)", "css").replace("Niveau(x):", "").strip()
        experience = safe_find("li:nth-child(3)", "css").replace("Expérience:", "").strip()
        lieu = safe_find("li:nth-child(4)", "css").replace("Lieu:", "").strip()
        date_publication = safe_find("li:nth-child(5) span", "css")
        date_limite = safe_find("li:nth-child(6) span", "css")

        # Formatage des données pour insertion
        job_data = (
            job_title, metiers, niveau, experience, lieu,
            date_publication, date_limite, url
        )

        return job_data

    except Exception as e:
        print(f"Erreur lors de l'extraction pour l'URL {url} : {e}")
        return None

    finally:
        driver.quit()

# Fonction principale
def scrape_jobs_to_csv(home_url):
    """Scrape toutes les offres d'emploi depuis la page principale."""
    print("Début de l'extraction des offres...")
    create_csv()

    # Récupérer les URLs des offres
    job_urls = get_job_urls(home_url)
    print(f"{len(job_urls)} offres trouvées.")

    for url in job_urls:
        print(f"Scraping : {url}")
        scraped_data = scrape_job_details(url)
        if scraped_data:
            append_to_csv(scraped_data)
        time.sleep(1)  # Délai pour éviter d'être bloqué

    print(f"Extraction terminée. Les données ont été sauvegardées dans {csv_file}.")

# Appel principal
if __name__ == "__main__":
    HOME_URL = "https://emploi.educarriere.ci/"  # URL de la page principale
    scrape_jobs_to_csv(HOME_URL)
