"""
Étape 3 — Validation du journal alimentaire
Prompt : génération d'un scénario parmi les alternatives possibles
Extracteurs : scénario retenu + conclusion clinique courte
"""

from core.extract import extract_between


def build_validation_prompt(journal: str, correction: str = "") -> str:
    correction_block = ""
    if correction:
        correction_block = (
            f"\n⚠️ CORRECTION OBLIGATOIRE DU NUTRITIONNISTE — À appliquer en priorité absolue :\n"
            f"{correction}\n"
            f"Tu dois impérativement tenir compte de cette correction. "
            f"Si tu ne l'appliques pas, ta réponse sera incorrecte.\n"
        )

    return f"""Tu es un nutritionniste. Langue: français.
{correction_block}
Voici un journal alimentaire:
{journal}

Instructions:
1. Lis le journal et identifie UNIQUEMENT les moments de repas réellement présents dans le journal (ne suppose pas de structure fixe — le patient peut manger 1, 2, 3 repas ou plus, à n'importe quelle heure).
2. Pour chaque moment de repas identifié, repère les groupes d'alternatives (séparés par "/", "ou", "או" en hébreu, ou toute autre formulation indiquant un choix).
3. Applique la correction du nutritionniste ci-dessus si elle existe.
4. Génère UN SEUL scénario journalier plausible : pour chaque groupe d'alternatives, choisis UN SEUL aliment. Ne crée pas de repas qui n'existent pas dans le journal.
5. Affiche le scénario structuré repas par repas, dans l'ordre chronologique du journal, avec l'heure ou le contexte si disponible (ex: "Repas du matin — 7h30", "Repas du midi", "Collation — 16h", etc.).

Format de sortie :

###SCENARIO_START###
[Pour chaque repas identifié dans le journal, une section du type :]
[emoji pertinent] [Intitulé du repas tel qu'il ressort du journal] (heure si disponible) :
- aliment retenu
- aliment retenu
[Répéter pour chaque repas identifié, sans en inventer]
###SCENARIO_END###

Enfin, génère une conclusion clinique brève:
###CONCLUSION_VAL_START###
[2-3 phrases max: nombre de repas identifiés dans ce journal, aliments protéiques principaux retenus, nombre de groupes d'alternatives traités]
###CONCLUSION_VAL_END###"""


def extract_scenario(text: str):
    return extract_between(text, "###SCENARIO_START###", "###SCENARIO_END###")


def extract_validation_conclusion(text: str):
    return extract_between(text, "###CONCLUSION_VAL_START###", "###CONCLUSION_VAL_END###")
