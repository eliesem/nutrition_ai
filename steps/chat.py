"""
Chat — Questions de suivi
Prompt : nutritionniste clinique, réponses courtes (5 lignes max)
"""


def build_chat_messages(analysis_context: str, history: list, question: str) -> list:
    return [
        {
            "role": "system",
            "content": (
                "Tu es un nutritionniste spécialisé en néphrologie clinique. Réponds en français. "
                "Limite ta réponse à 5 lignes maximum avec les points les plus importants sous forme de liste à puces. "
                "Contexte de l'analyse:\n" + analysis_context
            ),
        },
        *history,
        {"role": "user", "content": question},
    ]
