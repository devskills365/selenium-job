import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Étape 1 : Configurer le WebDriver
driver_path = "C:\\Users\\DELL\\Desktop\\selenium\\chromedriver-win64\\chromedriver.exe"
service = Service(driver_path)
driver = webdriver.Chrome(service=service)

# Étape 2 : Ouvrir l'URL de base
base_url = "https://www.agenceemploijeunes.ci/site/offres-emplois?page="
driver.get(base_url + "1")  # Charger la première page

# Pause initiale pour chargement
time.sleep(5)

# Étape 3 : Initialiser une liste pour stocker les données
job_offers = []

# Fonction pour extraire les informations d'une page
def extract_offers():
    offers = driver.find_elements(By.CLASS_NAME, "job-post-info")
    for offer in offers:
        try:
            # Titre et lien du poste
            title_element = offer.find_element(By.TAG_NAME, "h4").find_element(By.TAG_NAME, "a")
            title = title_element.text.strip()
            link = title_element.get_attribute("href")

            # Dates et localisation
            published_date_element = offer.find_element(By.XPATH, "//*[@id='offre_aej']/ul/li[1]/div/div[1]/div[2]/ul/div/li[1]")
            published_date = published_date_element.text.split(":")[1].strip()

            deadline_date_element = offer.find_element(By.XPATH, "//*[@id='offre_aej']/ul/li[1]/div/div[1]/div[2]/ul/div/li[2]")
            deadline_date = deadline_date_element.text.split(":")[1].strip()

            location_element = offer.find_element(By.XPATH, "//*[@id='offre_aej']/ul/li[1]/div/div[1]/div[2]/ul/div/li[3]")
            location = location_element.text.strip()

            description_element = offer.find_element(By.XPATH, "//*[@id='offre_aej']/ul/li[1]/div/p")
            description = description_element.text.strip()

            # Ajouter l'offre à la liste
            job_offers.append({
                "Titre": title,
                "Lien": link,
                "Publié le": published_date,
                "Date limite": deadline_date,
                "Localisation": location,
                "Description": description
            })

        except Exception as e:
            print("Erreur lors de l'extraction d'une offre :", e)

# Étape 4 : Parcourir les pages de 1 à 10
for page in range(1, 11):  # De 1 à 10
    url = base_url + str(page)
    driver.get(url)
    
    # Attendre que les éléments soient visibles
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "job-post-info"))
    )
    
    # Extraire les offres visibles sur la page actuelle
    extract_offers()

    # Attendre que la page soit complètement chargée avant de passer à la suivante
    time.sleep(3)  # Temps d'attente réduit à 3 secondes

# Étape 5 : Sauvegarder les données dans un fichier CSV
csv_file = "job_offers.csv"

# En-têtes des colonnes
headers = ["Titre", "Lien", "Publié le", "Date limite", "Localisation", "Description"]

# Ouvrir le fichier CSV en mode écriture
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=headers)
    
    # Écrire l'en-tête dans le fichier CSV
    writer.writeheader()
    
    # Écrire les données des offres dans le fichier
    for job in job_offers:
        writer.writerow(job)

print(f"Les données ont été sauvegardées dans {csv_file}")

# Étape 6 : Fermer le navigateur
driver.quit()
