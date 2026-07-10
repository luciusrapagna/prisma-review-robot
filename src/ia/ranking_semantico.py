import os
import math
import re
from collections import Counter
import statistics

import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


hf_token = os.getenv("HF_TOKEN") or os.getenv("HF_HUB_TOKEN")

if hf_token:
    os.environ["HF_TOKEN"] = hf_token
    os.environ["HF_HUB_TOKEN"] = hf_token


modelo = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)


def _texto_valido(valor):
    if valor is None:
        return ""

    if isinstance(valor, float) and math.isnan(valor):
        return ""

    texto = str(valor).strip()

    if texto.lower() in {"nan", "none", "null"}:
        return ""

    return texto


def _similaridade_float(valor, padrao=0.30):
    try:
        if isinstance(valor, str):
            valor = valor.replace(",", ".").strip()

        return float(valor)

    except Exception:
        return padrao


def _campo(artigo, *nomes):
    for nome in nomes:
        valor = artigo.get(nome)

        if valor not in [None, ""]:
            return valor

    return ""


def _titulo_suspeito(titulo):
    titulo = _texto_valido(titulo).lower()
    titulo = re.sub(r"\s+", " ", titulo).strip()

    titulos_ruins = {
        "abstract",
        "abstract title page",
        "title page",
        "contents",
        "table of contents",
        "editorial board",
        "front matter",
        "author index",
        "subject index",
        "untitled",
        "sem título",
        "sem titulo",
    }

    if titulo in titulos_ruins:
        return True

    if len(titulo) < 15:
        return True

    return False


def _montar_texto_artigo(artigo):
    """
    Constrói o texto interno usado pelo ranking semântico.

    Prioridade científica:
    1. Título
    2. Resumo
    3. Palavras-chave / descritores

    Esses campos são usados apenas internamente e não precisam
    aparecer nas tabelas exportadas.
    """

    titulo = _texto_valido(
        _campo(
            artigo,
            "Titulo",
            "Título",
            "titulo",
            "title",
        )
    )

    resumo = _texto_valido(
        _campo(
            artigo,
            "Resumo",
            "resumo",
            "abstract",
            "Abstract",
        )
    )

    palavras_chave = _texto_valido(
        _campo(
            artigo,
            "Palavras-chave",
            "Palavras_chave",
            "PalavrasChave",
            "palavras_chave",
            "keywords",
            "Keywords",
            "keyword",
            "Descritores",
            "descritores",
            "descriptors",
        )
    )

    if _titulo_suspeito(titulo):
        return "", "titulo_suspeito"

    partes = []

    if titulo:
        # Título recebe peso maior no embedding.
        partes.extend([titulo, titulo])

    if resumo:
        partes.append(resumo)

    if palavras_chave:
        # Palavras-chave recebem reforço moderado.
        partes.extend([
            palavras_chave,
            palavras_chave,
        ])

    texto = ". ".join(
        parte for parte in partes if parte
    ).strip()

    if resumo and palavras_chave:
        fonte_texto = "titulo_resumo_palavras_chave"
    elif resumo:
        fonte_texto = "titulo_resumo"
    elif palavras_chave:
        fonte_texto = "titulo_palavras_chave"
    else:
        fonte_texto = "titulo"

    return texto, fonte_texto


def _chave_artigo(artigo):
    doi = _texto_valido(
        _campo(artigo, "DOI", "doi")
    ).lower()

    if doi:
        doi = doi.replace("https://doi.org/", "")
        doi = doi.replace("http://doi.org/", "")
        return f"doi:{doi}"

    titulo = _texto_valido(
        _campo(
            artigo,
            "Titulo",
            "Título",
            "titulo",
            "title",
        )
    ).lower()

    titulo = re.sub(r"\s+", " ", titulo).strip()

    if titulo:
        return f"titulo:{titulo}"

    return ""


def calcular_similaridade(
    tema,
    artigos,
    similaridade_minima=0.30,
):
    if not artigos:
        return []

    similaridade_minima = _similaridade_float(
        similaridade_minima,
        0.30,
    )

    textos = []
    artigos_validos = []

    cont_titulo_resumo = 0
    cont_titulo = 0
    cont_sem_texto = 0
    cont_ruido = 0

    distribuicao_entrada = Counter(
        str(
            _campo(a, "Base", "base")
            or "Não informado"
        )
        for a in artigos
        if isinstance(a, dict)
    )

    print("\n" + "=" * 70)
    print("ATHENA PRISMA — RANKING SEMÂNTICO MULTIBASE")
    print("=" * 70)
    print(
        f"Distribuição antes do ranking: "
        f"{dict(distribuicao_entrada)}"
    )

    for artigo in artigos:
        texto, fonte_texto = _montar_texto_artigo(
            artigo
        )

        if fonte_texto == "titulo_suspeito":
            cont_ruido += 1
            continue

        if len(texto) < 5:
            cont_sem_texto += 1
            continue

        artigo["Fonte_Texto_Semantico"] = (
            fonte_texto
        )

        if fonte_texto == "titulo_resumo":
            cont_titulo_resumo += 1
        else:
            cont_titulo += 1

        textos.append(texto)
        artigos_validos.append(artigo)

    if not textos:
        print(
            "\nNenhum artigo com texto suficiente "
            "para filtro semântico."
        )
        return []

    print(
        f"Artigos válidos para embeddings: "
        f"{len(artigos_validos)}"
    )

    embeddings_artigos = modelo.encode(
        textos,
        show_progress_bar=False,
    )

    embedding_tema = modelo.encode(
        [str(tema)],
        show_progress_bar=False,
    )

    similaridades = cosine_similarity(
        embedding_tema,
        embeddings_artigos,
    )[0]

    todos_com_score = []
    artigos_filtrados = []

    for artigo, score in zip(
        artigos_validos,
        similaridades,
    ):
        score = round(float(score), 4)

        artigo["Score_Semantico"] = score

        todos_com_score.append(artigo)

        if score >= similaridade_minima:
            artigo["Status_Triagem"] = (
                "Incluído por corte semântico"
            )
            artigos_filtrados.append(artigo)

    distribuicao_corte = Counter(
        str(
            _campo(a, "Base", "base")
            or "Não informado"
        )
        for a in artigos_filtrados
    )

    print(
        f"Distribuição após corte principal: "
        f"{dict(distribuicao_corte)}"
    )

    # -------------------------------------------------
    # AUDITORIA ESTATÍSTICA DOS SCORES POR BASE
    # -------------------------------------------------

    grupos_scores = {}

    for artigo in todos_com_score:
        base = str(
            _campo(artigo, "Base", "base")
            or "Não informado"
        ).strip()

        score = float(
            artigo.get("Score_Semantico", 0)
        )

        grupos_scores.setdefault(base, []).append(score)

    print("\nAUDITORIA DOS SCORES POR BASE")

    estatisticas_bases = {}

    for base, scores in sorted(grupos_scores.items()):
        scores_ordenados = sorted(scores)

        n = len(scores_ordenados)
        minimo = min(scores_ordenados)
        maximo = max(scores_ordenados)
        media = statistics.mean(scores_ordenados)
        mediana = statistics.median(scores_ordenados)

        q75_idx = min(
            n - 1,
            int(round((n - 1) * 0.75))
        )

        q90_idx = min(
            n - 1,
            int(round((n - 1) * 0.90))
        )

        q75 = scores_ordenados[q75_idx]
        q90 = scores_ordenados[q90_idx]

        acima_corte = sum(
            1 for s in scores_ordenados
            if s >= similaridade_minima
        )

        estatisticas_bases[base] = {
            "n": n,
            "min": minimo,
            "media": media,
            "mediana": mediana,
            "q75": q75,
            "q90": q90,
            "max": maximo,
            "acima_corte": acima_corte,
        }

        print(
            f"{base}: "
            f"n={n} | "
            f"mín={minimo:.4f} | "
            f"média={media:.4f} | "
            f"mediana={mediana:.4f} | "
            f"Q75={q75:.4f} | "
            f"Q90={q90:.4f} | "
            f"máx={maximo:.4f} | "
            f"acima do corte={acima_corte}"
        )

    # -------------------------------------------------
    # RESGATE MULTIBASE CIENTIFICAMENTE CONTROLADO
    # -------------------------------------------------
    #
    # Só recupera artigos:
    # - de bases não representadas adequadamente;
    # - com score mínimo aceitável;
    # - sem duplicação;
    # - limitados aos melhores resultados por base.
    #
    # Não força inclusão de artigos irrelevantes.
    # -------------------------------------------------

    # -------------------------------------------------
    # RESGATE MULTIBASE ADAPTATIVO
    # -------------------------------------------------
    #
    # Critério:
    # 1. Mantém todos que passaram pelo corte principal.
    # 2. Para cada base secundária, considera o melhor entre:
    #    - 70% do corte principal;
    #    - percentil 90 dos scores daquela própria base.
    # 3. Nunca aceita score abaixo de 0.15.
    # 4. Limita o resgate a 20 artigos por base.
    #
    # Assim, a diversidade não é artificial: entram apenas
    # os melhores registros disponíveis dentro de cada fonte.
    # -------------------------------------------------

    limite_por_base = 20

    bases_resgate = [
        "Crossref",
        "OpenAlex",
        "Semantic Scholar",
        "SciELO",
        "LILACS",
    ]

    chaves_incluidas = {
        _chave_artigo(a)
        for a in artigos_filtrados
        if _chave_artigo(a)
    }

    for base in bases_resgate:
        scores_base = [
            float(a.get("Score_Semantico", 0))
            for a in todos_com_score
            if str(
                _campo(a, "Base", "base")
            ).strip().lower() == base.lower()
        ]

        if not scores_base:
            print(
                f"Resgate {base}: "
                f"nenhum candidato disponível."
            )
            continue

        scores_ordenados = sorted(scores_base)

        n_scores = len(scores_ordenados)

        q90_idx = min(
            n_scores - 1,
            int(round((n_scores - 1) * 0.90))
        )

        q90_base = scores_ordenados[q90_idx]

        corte_base = max(
            0.15,
            min(
                similaridade_minima * 0.70,
                q90_base
            )
        )

        candidatos = [
            a
            for a in todos_com_score
            if str(
                _campo(a, "Base", "base")
            ).strip().lower() == base.lower()
            and float(
                a.get("Score_Semantico", 0)
            ) >= corte_base
        ]

        candidatos.sort(
            key=lambda a: float(
                a.get("Score_Semantico", 0)
            ),
            reverse=True,
        )

        adicionados = 0

        for artigo in candidatos:
            if adicionados >= limite_por_base:
                break

            chave = _chave_artigo(artigo)

            if not chave:
                continue

            if chave in chaves_incluidas:
                continue

            artigo["Status_Triagem"] = (
                "Incluído por resgate multibase adaptativo"
            )

            artigo["Corte_Resgate_Base"] = round(
                corte_base,
                4
            )

            artigos_filtrados.append(artigo)
            chaves_incluidas.add(chave)

            adicionados += 1

        print(
            f"Resgate {base}: "
            f"{adicionados} adicionados | "
            f"Q90={q90_base:.4f} | "
            f"corte adaptativo={corte_base:.4f}"
        )

    artigos_ordenados = sorted(
        artigos_filtrados,
        key=lambda x: float(
            x.get("Score_Semantico", 0)
        ),
        reverse=True,
    )

    distribuicao_final = Counter(
        str(
            _campo(a, "Base", "base")
            or "Não informado"
        )
        for a in artigos_ordenados
    )

    print("\nAUDITORIA SEMÂNTICA ATHENA")
    print(
        f"Avaliados com título + resumo: "
        f"{cont_titulo_resumo}"
    )
    print(
        f"Avaliados apenas com título: "
        f"{cont_titulo}"
    )
    print(
        f"Ignorados sem texto suficiente: "
        f"{cont_sem_texto}"
    )
    print(
        f"Ruídos editoriais removidos: "
        f"{cont_ruido}"
    )
    print(
        f"Artigos após triagem: "
        f"{len(artigos_ordenados)}"
    )
    print(
        f"Distribuição final por base: "
        f"{dict(distribuicao_final)}"
    )
    print("=" * 70 + "\n")

    return artigos_ordenados


def salvar_ranking_semantico(artigos):
    if not artigos:
        print("\nNenhum artigo para salvar.")
        return

    df = pd.DataFrame(artigos)

    caminho = (
        "outputs/tables/ranking_semantico.xlsx"
    )

    df.to_excel(
        caminho,
        index=False,
    )

    print(
        f"\nRanking semântico salvo em: "
        f"{caminho}"
    )
