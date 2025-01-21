from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time

# Configuration du driver (plus robuste)
driver_path = "C:\\Users\\DELL\\OneDrive - ENSEA\\Desktop\\selenium\\chromedriver-win64\\chromedriver.exe"
options = webdriver.ChromeOptions()
options.add_argument("--incognito")
# Pour éviter les erreurs liées à l'absence d'affichage (utile sur les serveurs)
# options.add_argument("--headless") # Décommenter si besoin
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Liste pour stocker les informations des annonces
job_listings = []

# Parcourir plusieurs pages
for i in range(1, 6):
    url = f"https://www.emploi.ci/recherche-jobs-cote-ivoire?page={i}"
    driver.get(url)
    print(f"Scraping page {i}: {url}")

    try:
        wait = WebDriverWait(driver, 60)  # Timeout augmenté à 20 secondes
        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "card-job-detail"))) # Attendre que TOUTES les cartes soient présentes
        time.sleep(2)  # Délai après le chargement des cartes

        job_cards = driver.find_elements(By.CLASS_NAME, "card-job-detail")

        if not job_cards:
            print("Aucune carte d'emploi trouvée sur cette page.")
            continue

        for card in job_cards:
            job_data = {}  # Initialiser un dictionnaire pour chaque offre

            try:
                job_data["Titre"] = card.find_element(By.XPATH, ".//h3/a").text.strip()
                job_data["Lien"] = card.find_element(By.XPATH, ".//h3/a").get_attribute("href")

                # Stratégie plus robuste pour l'entreprise
                try:
                    job_data["Entreprise"] = card.find_element(By.CLASS_NAME, "card-job-company").text.strip() # Correction du sélecteur
                except:
                    job_data["Entreprise"] = "Non spécifié"
                    print("Entreprise non trouvée pour cette offre.")

                job_data["Description"] = card.find_element(By.CLASS_NAME, "card-job-description").text.replace("+plus", "").strip()

                def extract_from_list(text_to_find):
                    try:
                        li_element = card.find_element(By.XPATH, f".//li[contains(text(), '{text_to_find}')]")
                        return li_element.text.split(":")[1].strip()
                    except:
                        return "Non spécifié"

                job_data["Niveau d'étude"] = extract_from_list("Niveau d´études requis")
                job_data["Expérience"] = extract_from_list("Niveau d'expérience")
                job_data["Contrat"] = extract_from_list("Contrat proposé")
                job_data["Lieu"] = extract_from_list("Région de")
                job_data["Compétences"] = extract_from_list("Compétences clés")

                job_listings.append(job_data)

            except Exception as inner_e:
                print(f"Erreur lors de l'extraction d'une annonce individuelle : {inner_e}")
                print(card.get_attribute('innerHTML')) # Affiche le HTML de la carte pour le débogage

    except Exception as outer_e:
        print(f"Erreur lors du chargement de la page {i}: {outer_e}")
# Fermer le navigateur
driver.quit()

# Enregistrer les résultats dans un fichier CSV
csv_filename = "emploi_ci_ok.csv"
with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ["Titre", "Entreprise", "Description", "Niveau d'étude", "Expérience", "Contrat", "Lieu", "Compétences", "Lien"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(job_listings) # Utilisation de writerows pour plus d'efficacité

print(f"Les résultats ont été enregistrés dans {csv_filename}")