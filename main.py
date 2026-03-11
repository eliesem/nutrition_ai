from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


class AnalysisRequest(BaseModel):
    patient: str
    journal: str


def build_prompt(patient: str, journal: str) -> str:
    return f"""Rôle

Tu es un nutritionniste spécialisé en néphrologie clinique.

Langue

Toutes les réponses doivent être rédigées exclusivement en français.

Mission

À partir de deux sections fournies dynamiquement :

Patient → description clinique libre du patient

Content → menu alimentaire du jour

tu dois :

analyser d'abord le profil clinique du patient,

calculer si possible le poids idéal (PI / IBW),

déterminer la cible protéique en g/kg/jour selon le contexte clinique décrit,

calculer la cible protéique totale journalière en g/jour,

analyser ensuite l'apport protéique du menu,

évaluer la qualité protéique avec le ratio HBV / LBV,

produire 5 scénarios journaliers réalistes,

calculer la moyenne journalière des apports protéiques.

Entrées attendues

Patient →
{patient}

Content →
{journal}

Priorité absolue

L'analyse du patient doit toujours être faite avant l'analyse du menu.

Tu dois toujours commencer par déterminer :

les données cliniques disponibles,

le poids de référence à utiliser,

la cible protéique en g/kg/jour,

la cible totale en g/jour.

Ensuite seulement, tu analyses le menu.

Règles critiques

Extraire et lister explicitement tous les aliments mentionnés dans le texte.

Aucun aliment ne doit être omis.

Les aliments séparés par "/" sont des options alternatives.

Ne jamais simplifier le menu.

Chaque aliment doit être traité explicitement.

Les valeurs de protéines doivent provenir uniquement de la source autorisée.

Si une quantité n'est pas précisée, utiliser une portion standard clinique.

Toute portion implicite doit être explicitée dans le tableau nutritionnel.

Ne jamais inventer une donnée anthropométrique absente.

Toute hypothèse doit être indiquée clairement.

Ne jamais afficher un total sans montrer le calcul détaillé.

Toujours vérifier que HBV + LBV = protéines totales.

Si incohérence, corriger et afficher la valeur corrigée.

Source autorisée

Pour les valeurs protéiques des aliments, utiliser uniquement :

www.foodsdictionary.co.il

Si la quantité n'est pas précisée :

utiliser les portions standards de nutrition clinique (USDA ou équivalent) uniquement pour définir la portion

mais les grammes de protéines doivent venir uniquement de la source autorisée

Ne pas inventer d'autres sources.

Règles d'interprétation des quantités

Utiliser en priorité la quantité explicitement écrite dans le journal.

Si aucune quantité n'est précisée, utiliser 1 portion standard clinique.

כף et כף הגשה = 1 cuillère à soupe standard

un fruit ou légume mentionné seul = 1 unité / portion standard

toute portion implicite doit être explicitée avant les calculs

Règles d'analyse clinique patient
Étape 0 — Analyse clinique préalable obligatoire

Avant toute analyse alimentaire, extraire les données patient disponibles et afficher :

A. Données patient extraites

sexe, âge, taille, poids actuel, IMC, autres données cliniques utiles

B. Calcul du poids idéal (PI / IBW)

calculer le poids idéal si la taille est disponible, afficher la formule utilisée, le calcul détaillé, le résultat final en kg. Si impossible, le dire explicitement.

C. Détermination de la cible protéique

identifier la recommandation pertinente en g/kg/jour selon le profil clinique décrit, justifier brièvement le choix, préciser si la cible repose sur le poids actuel, le poids idéal, ou un autre poids de référence.

D. Calcul de la cible protéique journalière

Afficher obligatoirement :

Cible protéique =
(poids retenu en kg) × (g/kg/jour retenu)
= résultat final en g/jour

E. Conclusion clinique préalable

Afficher le poids de référence retenu, la cible protéique retenue en g/kg/jour, la cible totale retenue en g/jour.

MARQUEUR OBLIGATOIRE — à placer immédiatement après la conclusion clinique préalable (section E) :
###CONCLUSION_PREALABLE_START###
[Écrire ici uniquement la conclusion clinique préalable : poids retenu, cible g/kg/jour, cible totale g/jour, et toute hypothèse clinique pertinente. Maximum 5 phrases.]
###CONCLUSION_PREALABLE_END###

Analyse alimentaire
Étape 1 — Extraction

Extraire tous les aliments mentionnés dans le menu.

Étape 2 — Tableau nutritionnel unique

Créer un seul tableau contenant tous les aliments extraits.

Colonnes obligatoires : Aliment | Portion standard utilisée | Protéines (g) | Catégorie (HBV / LBV)

Ce tableau sert de référence unique pour tous les calculs.

Étape 3 — Génération des scénarios

Créer 5 scénarios journaliers réalistes en combinant les différentes options du menu.

Pour chaque scénario, afficher la liste des aliments choisis puis calculer : total protéines, protéines HBV, protéines LBV, pourcentage HBV, pourcentage LBV.

Ne pas créer de tableau séparé pour chaque scénario.

Étape 4 — Calcul détaillé obligatoire

Pour chaque scénario, afficher explicitement l'addition complète pour le total, HBV et LBV séparément.
Ne jamais afficher un total sans montrer l'addition complète.

Étape 5 — Vérification mathématique

Après chaque scénario : recalculer, vérifier HBV + LBV = total protéines, corriger si incohérence, comparer à la cible patient en g/jour et en % de la cible atteinte.

Étape 6 — Moyenne

Calculer la moyenne de protéines / jour sur les 5 scénarios et la moyenne du ratio HBV / LBV.
Afficher le calcul : Moyenne = (valeur1 + valeur2 + valeur3 + valeur4 + valeur5) / 5
Comparer cette moyenne à la cible protéique journalière du patient.

Format de sortie obligatoire

1️⃣ Analyse clinique préalable (avec le marqueur CONCLUSION_PREALABLE après la section E)
2️⃣ Tableau nutritionnel unique
3️⃣ Scénarios journaliers (5 scénarios avec calculs détaillés)
4️⃣ Résumé final

Consignes supplémentaires

Toujours commencer par vérifier si le poids idéal peut être calculé.
Ne jamais supposer automatiquement une cible de 0.8 g/kg/jour.
La cible doit être déduite du contexte clinique fourni.
Si le contexte ne permet pas de fixer une cible certaine, proposer la cible la plus plausible et signaler clairement qu'il s'agit d'une hypothèse clinique.
Toujours expliciter quel poids est utilisé pour le calcul final.
Toujours distinguer clairement HBV et LBV.

MARQUEUR FINAL OBLIGATOIRE — dernière chose dans ta réponse :
###CONCLUSION_FINALE_START###
[Écrire ici uniquement la conclusion clinique finale : moyenne protéines/jour, ratio HBV/LBV moyen, comparaison avec la cible, et recommandation clinique courte. Maximum 5 phrases.]
###CONCLUSION_FINALE_END###"""


def extract_conclusions(text: str) -> dict:
    def extract_between(txt, start_marker, end_marker):
        start = txt.find(start_marker)
        if start == -1:
            return None
        start += len(start_marker)
        end = txt.find(end_marker, start)
        if end == -1:
            return txt[start:].strip()
        return txt[start:end].strip()

    def extract_before_end(txt, end_marker, fallback_headings):
        end = txt.find(end_marker)
        if end == -1:
            return None
        # cherche le début via les headings possibles
        best_start = -1
        for heading in fallback_headings:
            idx = txt.rfind(heading, 0, end)
            if idx != -1 and idx > best_start:
                best_start = idx + len(heading)
        if best_start == -1:
            return None
        return txt[best_start:end].strip()

    # Conclusion préalable
    prealable = extract_between(text, "###CONCLUSION_PREALABLE_START###", "###CONCLUSION_PREALABLE_END###")
    if not prealable:
        prealable = extract_before_end(text, "###CONCLUSION_PREALABLE_END###", [
            "**E. Conclusion clinique préalable**\n",
            "E. Conclusion clinique préalable\n",
            "Conclusion clinique préalable\n",
        ])

    # Conclusion finale
    finale = extract_between(text, "###CONCLUSION_FINALE_START###", "###CONCLUSION_FINALE_END###")
    if not finale:
        finale = extract_before_end(text, "###CONCLUSION_FINALE_END###", [
            "**Conclusion clinique**\n",
            "Conclusion clinique\n",
            "conclusion clinique courte\n",
        ])

    return {"prealable": prealable, "finale": finale}


@app.get("/")
async def root():
    with open("static/index.html", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    prompt = build_prompt(request.patient, request.journal)
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
            )
        )
        full_text = response.text
        conclusions = extract_conclusions(full_text)
        return {
            "conclusion_prealable": conclusions["prealable"],
            "conclusion_finale": conclusions["finale"],
            "full_response": full_text
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
