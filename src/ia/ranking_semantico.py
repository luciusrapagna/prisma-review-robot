import os
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# Configurar token do Hugging Face para evitar avisos de autenticação
hf_token = os.getenv('HF_TOKEN') or os.getenv('HF_HUB_TOKEN')
if hf_token:
    os.environ['HF_TOKEN'] = hf_token
    os.environ['HF_HUB_TOKEN'] = hf_token

modelo = SentenceTransformer(
    'sentence-transformers/all-MiniLM-L6-v2'
)


def calcular_similaridade(
    tema,
    artigos,
    similaridade_minima=0.30
):

    if not artigos:
        return []

    textos = []

    for artigo in artigos:

        titulo = artigo.get("Título", "")
        resumo = artigo.get("Resumo", "")

        texto = f"{titulo}. {resumo}"

        textos.append(texto)

    embeddings_artigos = modelo.encode(textos)

    embedding_tema = modelo.encode([tema])

    similaridades = cosine_similarity(
        embedding_tema,
        embeddings_artigos
    )[0]

    artigos_filtrados = []

    for artigo, score in zip(artigos, similaridades):

        score = round(float(score), 4)

        artigo["Score_Semantico"] = score

        if score >= similaridade_minima:
            artigos_filtrados.append(artigo)

    artigos_ordenados = sorted(
        artigos_filtrados,
        key=lambda x: x["Score_Semantico"],
        reverse=True
    )

    print(
        f"\nArtigos após filtro semântico "
        f"(>= {similaridade_minima}): "
        f"{len(artigos_ordenados)}"
    )

    return artigos_ordenados


def salvar_ranking_semantico(artigos):

    if not artigos:
        print("\nNenhum artigo para salvar.")
        return

    df = pd.DataFrame(artigos)

    caminho = "outputs/tables/ranking_semantico.xlsx"

    df.to_excel(caminho, index=False)

    print(f"\nRanking semântico salvo em: {caminho}")