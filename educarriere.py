from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
from selenium.webdriver.chrome.options import Options

# Configuration
driver_path = "C:\\Users\\DELL\\OneDrive - ENSEA\\Desktop\\selenium\\chromedriver-win64\\chromedriver.exe"  # À ADAPTER ABSOLUMENT !
csv_filename = "emploi_educarriere_ci_ok.csv"
base_url = "https://emploi.educarriere.ci/emploi/page/emploi/"
start_page = 1
end_page = 26  # Ajustez selon le nombre de pages à scraper
max_retries = 3
retry_delay = 5
timeout = 60  # Timeout global pour les opérations Selenium

# Options du navigateur (anti-détection renforcée)
options = Options()
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36")
# options.add_argument("--headless=new")  # Mode sans interface graphique (décommenter pour l'utiliser)
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--disable-extensions")
options.add_argument("--disable-popup-blocking")
options.add_argument("--disable-notifications")
options.add_argument("--log-level=3")  # Réduire les logs du navigateur

# Initialisation du driver (avec gestion des erreurs critiques)
try:
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
except WebDriverException as e:
    print(f"Erreur CRITIQUE lors de l'initialisation du WebDriver : {e}")
    exit()

job_listings = []

def extract_from_list(card, text_to_find):
    try:
        li_element = WebDriverWait(card, timeout).until(EC.presence_of_element_located((By.XPATH, f".//li[contains(., '{text_to_find}')]")))
        return li_element.text.split(":")[1].strip() if ":" in li_element.text else "Non spécifié"
    except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
        return "Non spécifié"

def scrape_page(url):
    retries = 0
    while retries < max_retries:
        try:
            print(f"Scraping page: {url} (Tentative {retries + 1})")
            driver.get(url)

            WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".rt-post h4.post-title a"))) #attente plus précise
            time.sleep(2) #Attendre le chargement des éléments dynamiques

            cards = driver.find_elements(By.CSS_SELECTOR, ".rt-post")
            if not cards:
                print("Aucune offre trouvée sur cette page.")
                return True

            for card in cards:
                job_data = {}
                try:
                    job_data["Titre"] = card.find_element(By.XPATH, ".//h4/a").text.strip()
                    job_data["Lien"] = card.find_element(By.XPATH, ".//h4/a").get_attribute("href")

                    job_listings.append(job_data)

                except (NoSuchElementException, TimeoutException, StaleElementReferenceException) as e:
                    print(f"Erreur lors de l'extraction des données d'une offre : {e}")
                    print(card.get_attribute('innerHTML') if card else "Carte non disponible pour le debug") #protection si la card n'existe pas
                except Exception as e:
                    print(f"Erreur inattendue lors de l'extraction d'une offre: {e}")
                    print(card.get_attribute('innerHTML')if card else "Carte non disponible pour le debug")

            return True  # Page scrapée avec succès

        except TimeoutException:
            print(f"Délai d'attente dépassé pour {url}. Réessai dans {retry_delay} secondes...")
            retries += 1
            time.sleep(retry_delay)
        except WebDriverException as e:
            print(f"Erreur WebDriver pour {url}: {e}. Réessai dans {retry_delay} secondes...")
            retries += 1
            time.sleep(retry_delay)
        except Exception as e:
            print(f"Erreur inattendue lors du chargement de {url}: {e}. Réessai dans {retry_delay} secondes...")
            retries += 1
            time.sleep(retry_delay)

    print(f"Échec du scraping de {url} après {max_retries} tentatives.")
    return False

try:
    for page_num in range(start_page, end_page + 1):
        url = base_url + str(page_num)
        if not scrape_page(url):
            print(f"Arrêt du scraping après plusieurs erreurs consécutives sur la page {page_num}.")
            break

finally:
    driver.quit()

# Sauvegarde CSV (avec gestion du cas où aucune donnée n'a été extraite)
if job_listings:
    try:
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = job_listings[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(job_listings)
        print(f"Données enregistrées dans {csv_filename}")
    except Exception as e:
        print(f"Erreur lors de l'écriture du CSV : {e}")
else:
    print("Aucune donnée à enregistrer.")