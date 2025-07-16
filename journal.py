# Import des modules nécessaires
import os
import webbrowser
import requests
import random
import feedparser
import re
import locale
from datetime import datetime
from deep_translator import GoogleTranslator
from data import get_random_words, get_random_proverbs, get_random_activity

# Configuration de la langue pour avoir la date en français
try:
    locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
except:
    try:
        locale.setlocale(locale.LC_TIME, "French_France.1252")
    except:
        print("⚠️ Impossible d’activer la locale française.")

# Informations de base
CITY = "Paris"
LATITUDE = 48.8566
LONGITUDE = 2.3522
TODAY = datetime.now().strftime("%d %B %Y")

# Flux RSS pour les actualités
RSS_FR = "https://www.lemonde.fr/rss/une.xml"
RSS_AR = "https://www.aljazeera.net/aljazeerarss/ar.xml"

# Obtenir la météo actuelle grâce à l’API open-meteo
def get_weather(lat, lon):
    try:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true&temperature_unit=celsius"
        data = requests.get(url).json()
        temp = data["current_weather"]["temperature"]
        code = data["current_weather"]["weathercode"]

        descriptions = {
            0: "Clair", 1: "Principalement clair", 2: "Partiellement nuageux", 3: "Nuageux",
            45: "Brouillard", 48: "Brouillard givrant", 51: "Bruine légère", 53: "Bruine modérée",
            55: "Bruine dense", 61: "Pluie faible", 63: "Pluie modérée", 65: "Pluie forte",
            71: "Neige faible", 73: "Neige modérée", 75: "Neige forte", 80: "Averses",
            81: "Averses fortes", 82: "Averses violentes", 95: "Orages", 99: "Orages violents"
        }

        return f"{temp}°C, {descriptions.get(code, 'Inconnu')} ☀️"
    except:
        return "🌧️ Impossible d’obtenir la météo."

# Lire un flux RSS et extraire les titres, liens et images
def get_news_with_images_rss(url):
    feed = feedparser.parse(url)
    news = []
    for entry in feed.entries[:10]:
        title = entry.title
        link = entry.link
        image = None

        # Tentative pour récupérer une image associée à l’article
        if 'media_content' in entry:
            image = entry.media_content[0].get('url')
        elif 'media_thumbnail' in entry:
            image = entry.media_thumbnail[0].get('url')
        else:
            imgs = re.findall(r'<img[^>]+src="([^"]+)', entry.get('summary', ''))
            if imgs:
                image = imgs[0]

        news.append({"title": title, "link": link, "image": image})
    return news

# Formatage HTML d’une liste d’actualités avec images
def html_news_list(news_items):
    return ''.join(
        f'<li>{"<img src=\"" + item["image"] + "\" style=\"width:80px;vertical-align:middle;margin-right:10px;\">" if item["image"] else ""}'
        f'<a href="{item["link"]}" target="_blank">{item["title"]}</a></li>'
        for item in news_items
    )

# Récupérer les titres les plus populaires sur Hacker News, traduits en français
def get_hacker_news_fr():
    try:
        top_stories = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json").json()[:5]
        news = []
        for sid in top_stories:
            item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json").json()
            if item and "title" in item and "url" in item:
                title_fr = GoogleTranslator(source='en', target='fr').translate(item["title"])
                news.append({"title": title_fr, "link": item["url"]})
        return news
    except:
        return [{"title": "Actualités non disponibles", "link": "#"}]

# Génère une liste HTML de news Hacker News
def html_hacker_news(news):
    return ''.join(f'<li><a href="{item["link"]}" target="_blank">{item["title"]}</a></li>' for item in news)

# Obtenir une recette aléatoire depuis l’API TheMealDB
def get_random_recipe_info():
    try:
        url = "https://www.themealdb.com/api/json/v1/1/random.php"
        data = requests.get(url).json()
        meal = data["meals"][0]

        titre = meal["strMeal"]
        image = meal["strMealThumb"]
        lien = meal["strSource"] if meal["strSource"] else f"https://www.themealdb.com/meal/{meal['idMeal']}"

        ingredients = []
        for i in range(1, 21):
            ingredient = meal.get(f"strIngredient{i}")
            measure = meal.get(f"strMeasure{i}")
            if ingredient and ingredient.strip():
                ingredients.append(f"{measure.strip()} {ingredient.strip()}")

        return {
            "titre": titre,
            "image": image,
            "lien": lien,
            "ingredients": ingredients
        }
    except:
        return {
            "titre": "Recette non disponible",
            "image": "",
            "lien": "#",
            "ingredients": []
        }

# Mise en page HTML de la recette (image à droite, ingrédients à gauche)
def html_recette_section(recette):
    ingredients_html = "".join(f"<li>{ing}</li>" for ing in recette["ingredients"])
    return f"""
    <div class=\"section recette\">
        <strong>🥗 Recette du jour :</strong>
        <div class=\"recette-layout\">
            <div class=\"ingredients\">
                <ul>{ingredients_html}</ul>
            </div>
            <div class=\"image-recette\">
                <img src=\"{recette['image']}\" alt=\"Recette\" style=\"max-width: 300px; border-radius: 10px;\"><br>
                <a href=\"{recette['lien']}\" target=\"_blank\">{recette['titre']}</a>
            </div>
        </div>
    </div>
    """

# Récupération des données aléatoires
english_words_to_learn = get_random_words()
proverb_fr, proverb_ar = get_random_proverbs()
activity_maman = get_random_activity()
recette = get_random_recipe_info()
news_fr = get_news_with_images_rss(RSS_FR)
news_ar = get_news_with_images_rss(RSS_AR)
news_it = get_hacker_news_fr()

# Génération de la page HTML
html_content = f"""
<!DOCTYPE html>
<html lang=\"fr\">
<head>
    <meta charset=\"UTF-8\">
    <title>Mon Journal du {TODAY}</title>
    <link rel=\"stylesheet\" href=\"style.css\">
</head>
<body>
    <h1>🗞️ Mon Journal du {TODAY}</h1>

    <div class=\"section\"><strong>🌤️ Météo à {CITY} :</strong> {get_weather(LATITUDE, LONGITUDE)}</div>
    <div class=\"section\"><strong>📘 Proverbe FR :</strong> {proverb_fr}</div>
    <div class=\"section\"><strong>📙 مثل عربي :</strong> {proverb_ar}</div>

    <div class=\"section\"><strong>🇫🇷 Actualités France :</strong><ul>{html_news_list(news_fr)}</ul></div>
    <div class=\"section\"><strong>🌍 أخبار عربية :</strong><ul>{html_news_list(news_ar)}</ul></div>
    <div class=\"section\"><strong>🖥️ Actus Informatique :</strong><ul>{html_hacker_news(news_it)}</ul></div>

    <div class=\"section\">
        <strong>🎯 Mots anglais à apprendre :</strong>
        <ul>{''.join(f'<li><strong>{w["mot"]}</strong> : {w["definition"]}</li>' for w in english_words_to_learn)}</ul>
    </div>

    {html_recette_section(recette)}

    <div class=\"section\"><strong>👩‍👧 Activité maman :</strong> {activity_maman}</div>
    <div class=\"section\"><strong>🌌 Image du jour :</strong> <a href=\"https://apod.nasa.gov\" target=\"_blank\">NASA APOD</a></div>
</body>
</html>
"""

# Sauvegarde et ouverture automatique dans le navigateur
with open("mon_journal.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ Fichier HTML généré : mon_journal.html")
webbrowser.open(f"file://{os.path.abspath('mon_journal.html')}")
