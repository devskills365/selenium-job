from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv

# Configuration du driver
driver_path = "C:\\Users\\DELL\\Desktop\\selenium\\chromedriver-win64\\chromedriver.exe"
options = webdriver.ChromeOptions()
options.add_argument("--incognito")
options.add_argument("--disable-gpu")
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Liste pour stocker les informations des annonces
job_listings = []

# Parcourir plusieurs pages
for i in range(1, 5):
    url = f"https://www.agenceemploijeunes.ci/site/offres-emplois?page={i}"
    driver.get(url)

    # Attendre que les annonces soient chargées
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "post-bx")))

    # Récupérer toutes les annonces
    job_cards = driver.find_elements(By.CLASS_NAME, "post-bx")

    # Extraire les informations des annonces
    for card in job_cards:
        try:
            # Titre de l'annonce
            title = card.find_element(By.XPATH, ".//h4/a").text

            # Lien vers l'annonce
            link = card.find_element(By.XPATH, ".//h4/a").get_attribute("href")

            # Date de publication
            date_publication = card.find_element(By.XPATH, ".//ul/li[1]").text.split(":")[1].strip()

            # Date limite
            date_limit = card.find_element(By.XPATH, ".//ul/li[2]").text.split(":")[1].strip()

            # Localisation de l'emploi
            location = card.find_element(By.XPATH, ".//ul/li[3]").text.split(":")[1].strip()

            # Type d'emploi (CDD, THIMO, etc.)
            job_type = card.find_element(By.XPATH, ".//div[@class='job-time']/span").text.strip()

            # Diplôme requis
            diploma = card.find_element(By.XPATH, ".//div[@class='salary-bx']").text.split(":")[-1].strip()

            # Ajouter les informations à la liste
            job_listings.append({
                "Titre": title,
                "Lien": link,
                "Localisation": location,
                "Date limite": date_limit,
                "Date de publication": date_publication,
                "Type d'emploi": job_type,
                "Diplôme requis": diploma
            })
        except Exception as e:
            print(f"Erreur lors de l'extraction : {e}")

# Fermer le navigateur
driver.quit()

# Enregistrer les résultats dans un fichier CSV
with open("agence_emploi_jeunes_jobs.csv", 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ["Titre", "Lien", "Localisation", "Date limite", "Date de publication", "Type d'emploi", "Diplôme requis"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for job in job_listings:
        writer.writerow(job)

print("Les résultats ont été enregistrés dans agence_emploi_jeunes_jobs.csv")
