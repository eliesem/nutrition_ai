"""
Étape 4 — Analyse nutritionnelle complète
Prompt : calcul HBV/LBV, 3 scénarios, moyenne, conclusions
Extracteurs : conclusion préalable, conclusion finale, tableau nutritionnel
"""

from core.extract import extract_between


def build_analysis_prompt(journal: str, patient_context: str, correction: str = "") -> str:
    correction_section = ""
    if correction:
        correction_section = (
            f"\nCORRECTION DU NUTRITIONNISTE: {correction}\n"
            f"Tiens compte de cette correction dans l'analyse.\n"
        )

    return f"""Rôle

Tu es un nutritionniste spécialisé en néphrologie clinique.

Langue

Toutes les réponses doivent être rédigées exclusivement en français.

Mission

À partir des données fournies :
- Cible protéique déjà calculée (profil patient)
- Journal alimentaire du patient

tu dois :
analyser l'apport protéique du menu,
évaluer la qualité protéique avec le ratio HBV / LBV,
produire 3 scénarios journaliers réalistes,
calculer la moyenne journalière des apports protéiques.

Profil patient et cible protéique (déjà calculés):
{patient_context}
{correction_section}
Journal alimentaire:
{journal}

Règles critiques

Extraire et lister explicitement tous les aliments mentionnés dans le texte.

Aucun aliment ne doit être omis.

Les aliments séparés par "/" sont des options alternatives.
Le mot "או" en hébreu signifie "ou" et indique également des options alternatives, exactement comme "/". Traiter "או" comme un séparateur d'alternatives au même titre que "/".

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

MARQUEUR OBLIGATOIRE — à placer immédiatement après le rappel de la cible clinique :
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

Placer le tableau entre ces marqueurs :
###TABLE_START###
[tableau markdown ici]
###TABLE_END###

Étape 3 — Génération des scénarios

Créer 3 scénarios journaliers réalistes en combinant les différentes options du menu.

RÈGLE ABSOLUE pour les scénarios :
Avant de créer les scénarios, identifier et lister TOUS les groupes d'alternatives du journal (tous les groupes séparés par "/" ou par "או" en hébreu).
Dans chaque scénario, choisir exactement UN SEUL aliment par groupe d'alternatives.
Il est STRICTEMENT INTERDIT de prendre plusieurs aliments appartenant au même groupe d'alternatives, même si ces aliments apparaissent à des moments différents de la journée.
Un aliment qui apparaît dans un groupe d'alternatives n'est JAMAIS un aliment fixe — il est toujours une alternative.

Pour chaque scénario, afficher la liste des aliments choisis puis calculer : total protéines, protéines HBV, protéines LBV, pourcentage HBV, pourcentage LBV.

Ne pas créer de tableau séparé pour chaque scénario.

Étape 4 — Calcul détaillé obligatoire

Pour chaque scénario, afficher explicitement l'addition complète pour le total, HBV et LBV séparément.
Ne jamais afficher un total sans montrer l'addition complète.

Étape 5 — Vérification mathématique

Après chaque scénario : recalculer, vérifier HBV + LBV = total protéines, corriger si incohérence, comparer à la cible patient en g/jour et en % de la cible atteinte.

Étape 6 — Moyenne

Calculer la moyenne de protéines / jour sur les 3 scénarios et la moyenne du ratio HBV / LBV.
Afficher le calcul : Moyenne = (valeur1 + valeur2 + valeur3) / 3
Comparer cette moyenne à la cible protéique journalière du patient.

Format de sortie obligatoire

1️⃣ Rappel de la cible clinique patient (avec le marqueur CONCLUSION_PREALABLE)
2️⃣ Tableau nutritionnel unique (entre les marqueurs TABLE_START / TABLE_END)
3️⃣ Scénarios journaliers (3 scénarios avec calculs détaillés)
4️⃣ Résumé final

Consignes supplémentaires

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
    def _extract_before_end(txt, end_marker, fallback_headings):
        end = txt.find(end_marker)
        if end == -1:
            return None
        best_start = -1
        for heading in fallback_headings:
            idx = txt.rfind(heading, 0, end)
            if idx != -1 and idx > best_start:
                best_start = idx + len(heading)
        if best_start == -1:
            return None
        return txt[best_start:end].strip()

    prealable = extract_between(text, "###CONCLUSION_PREALABLE_START###", "###CONCLUSION_PREALABLE_END###")
    if not prealable:
        prealable = _extract_before_end(text, "###CONCLUSION_PREALABLE_END###", [
            "**E. Conclusion clinique préalable**\n",
            "E. Conclusion clinique préalable\n",
            "Conclusion clinique préalable\n",
        ])

    finale = extract_between(text, "###CONCLUSION_FINALE_START###", "###CONCLUSION_FINALE_END###")
    if not finale:
        finale = _extract_before_end(text, "###CONCLUSION_FINALE_END###", [
            "**Conclusion clinique**\n",
            "Conclusion clinique\n",
            "conclusion clinique courte\n",
        ])

    return {"prealable": prealable, "finale": finale}


def extract_table(text: str):
    return extract_between(text, "###TABLE_START###", "###TABLE_END###")
