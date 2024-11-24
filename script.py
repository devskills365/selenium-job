from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
"""
Ce code extraire les publication d'offres d'emploi sur le site emploi.ci et les stocks dans un fihciers csv pour une analyse profonde
"""
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
    url = f"https://www.emploi.ci/recherche-jobs-cote-ivoire?page={i}"
    driver.get(url)

    # Attendre que les annonces soient chargées
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "card-job-detail")))

    # Récupérer toutes les annonces
    job_cards = driver.find_elements(By.CLASS_NAME, "card")

    # Extraire les informations des annonces
    for card in job_cards:
        try:
            # Titre de l'annonce
            title = card.find_element(By.CSS_SELECTOR, "h3 a").text
            
            # Lien vers l'annonce
            link = card.find_element(By.CSS_SELECTOR, "h3 a").get_attribute("href")
            
            # Nom de l'entreprise
            company = card.find_element(By.CLASS_NAME, "card-job-company").text
            
            # Description de l'annonce
            description = card.find_element(By.CLASS_NAME, "card-job-description").text
            
            # Extraire les éléments de ul et li
            ul_elements = card.find_elements(By.CSS_SELECTOR, "ul li")
            ul_texts = [li.text for li in ul_elements]
            
            # Date de publication
            date_publication = card.find_element(By.CSS_SELECTOR, "time").get_attribute("datetime")

            # Ajouter les informations à la liste
            job_listings.append({
                "Titre": title,
                "Entreprise": company,
                "Lien": link,
                "Description": description,
                "Autres": "; ".join(ul_texts),
                "Date de publication": date_publication
            })
        except Exception as e:
            print(f"Erreur lors de l'extraction : {e}")

# Fermer le navigateur
driver.quit()

# Enregistrer les résultats dans un fichier CSV
with open("emploi_ci_jobs.csv", 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ["Titre", "Entreprise", "Lien", "Description", "Autres", "Date de publication"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for job in job_listings:
        writer.writerow(job)

print("Les résultats ont été enregistrés dans emploi_ci_jobs.csv")
