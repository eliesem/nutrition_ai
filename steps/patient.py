"""
Étape 1 — Profil patient
Prompt : analyse clinique + calcul g/kg/jour
Extracteurs : cible protéique (poids retenu, g/kg/j, total g/j)
"""

from core.extract import extract_between


def build_patient_prompt(patient: str, correction: str = "") -> str:
    correction_block = ""
    if correction:
        correction_block = (
            f"\n⚠️ CORRECTION DU NUTRITIONNISTE — À appliquer en priorité absolue :\n"
            f"{correction}\n"
        )

    return f"""Tu es un nutritionniste spécialisé en néphrologie clinique. Langue: français.
{correction_block}
Analyse ce profil patient et détermine la cible protéique.

Patient: {patient}

RÈGLE ABSOLUE — données incomplètes :
Si certaines données sont manquantes ou insuffisantes, tu NE DOIS PAS bloquer ni refuser de répondre.
Tu dois TOUJOURS produire une estimation avec les données disponibles, en utilisant des valeurs standards cliniques pour les paramètres manquants.
Indique clairement quels paramètres sont manquants et quelles hypothèses tu as faites.
Termine par une note du type : "⚠️ Données incomplètes — pour affiner ce calcul, il faudrait connaître : [liste des paramètres manquants]."

Étapes:
A. Données patient extraites (sexe, âge, taille, poids, IMC) — noter "non renseigné" si absent
B. Calcul poids idéal si possible (formule Lorentz ou Devine) — si données insuffisantes, utiliser le poids réel ou une estimation standard
C. Détermination cible protéique en g/kg/jour (justifiée cliniquement) — si contexte clinique incomplet, utiliser la recommandation standard la plus prudente et le signaler
D. Cible protéique = poids_retenu × g/kg/jour = total g/jour

MARQUEUR OBLIGATOIRE - place à la fin:
###PATIENT_TARGET###
poids_retenu_kg: [nombre]
target_g_per_kg: [nombre]
total_target_g: [nombre]
###END_PATIENT_TARGET###"""


def extract_patient_target(text: str) -> dict:
    block = extract_between(text, "###PATIENT_TARGET###", "###END_PATIENT_TARGET###")
    result = {"poids_retenu_kg": None, "target_g_per_kg": None, "total_target_g": None}
    if not block:
        return result
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("poids_retenu_kg:"):
            try:
                result["poids_retenu_kg"] = float(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        elif line.startswith("target_g_per_kg:"):
            try:
                result["target_g_per_kg"] = float(line.split(":", 1)[1].strip())
            except ValueError:
                pass
        elif line.startswith("total_target_g:"):
            try:
                result["total_target_g"] = float(line.split(":", 1)[1].strip())
            except ValueError:
                pass
    return result
