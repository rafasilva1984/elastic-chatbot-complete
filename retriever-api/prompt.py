SYSTEM_INSTRUCTIONS = (
    "Você é um assistente técnico. Responda com base APENAS no contexto fornecido. "
    "Se a resposta não estiver no contexto, diga que não encontrou evidências. "
    "Cite as fontes pelo título quando apropriado."
)

def build_prompt(question: str, context: str) -> str:
    return f"""{SYSTEM_INSTRUCTIONS}

Pergunta: {question}

Contexto:
{context}

Responda de forma curta, direta e cite as fontes se necessário.
"""
