import re
import html
from collections import Counter


def campo(artigo, *nomes):
    for n in nomes:
        v = artigo.get(n)
        if v not in [None, ""]:
            return v
    return ""


def limpar_texto(x):
    x = html.unescape(str(x or ""))
    x = re.sub(r"<[^>]+>", " ", x)
    x = re.sub(r"\s+", " ", x)
    return x.strip()


def texto_normalizado(x):
    return limpar_texto(x).lower()


PADROES_SUSPEITOS = [
    "abstract title page",
    "title page",
    "front matter",
    "table of contents",
    "contents",
    "editorial board",
    "author index",
    "subject index",
    "meeting abstracts",
    "conference abstracts",
    "poster abstracts",
    "supplement issue",
    "book of abstracts",
    "erratum",
    "corrigendum",
    "retracted",
    "withdrawn",
    "untitled",
    "sem título",
    "sem titulo",
    "arxiv",
    "cornell university",
    "institutional repository",
    "institutial research information system",
    "digital repository",
    "doctoral thesis",
    "phd thesis",
    "dissertation",
    "tese",
    "dissertação",
    "preprint",
]


def titulo_informativo(titulo):
    t = texto_normalizado(titulo)

    if not t:
        return False, "título ausente"

    if any(p in t for p in PADROES_SUSPEITOS):
        return False, "título/fonte suspeito"

    palavras = re.findall(r"[a-zA-ZÀ-ÿ0-9]+", t)

    if len(palavras) < 6:
        return False, "título pouco informativo"

    if len(t) < 35:
        return False, "título curto demais"

    return True, ""


def conteudo_suficiente(artigo):
    resumo = limpar_texto(
        campo(
            artigo,
            "Resumo",
            "resumo",
            "abstract",
            "Abstract",
        )
    )

    keywords = limpar_texto(
        campo(
            artigo,
            "Palavras-chave",
            "Palavras_chave",
            "PalavrasChave",
            "palavras_chave",
            "keywords",
            "Keywords",
            "Descritores",
            "descritores",
            "descriptors",
        )
    )

    base = str(
        campo(
            artigo,
            "Base",
            "base",
            "database",
        )
        or ""
    ).strip().lower()

    titulo = limpar_texto(
        campo(
            artigo,
            "Titulo",
            "Título",
            "titulo",
            "title",
        )
    )

    autores = limpar_texto(
        campo(
            artigo,
            "Autores",
            "autores",
            "authors",
            "author",
        )
    )

    revista = limpar_texto(
        campo(
            artigo,
            "Revista",
            "revista",
            "journal",
            "fonte",
            "venue",
        )
    )

    doi = limpar_texto(
        campo(
            artigo,
            "DOI",
            "doi",
        )
    )

    if len(resumo) >= 120:
        return True, ""

    quantidade_keywords = len(
        [
            termo
            for termo in re.split(
                r"[;,|]",
                keywords,
            )
            if termo.strip()
        ]
    )

    if quantidade_keywords >= 3:
        return True, ""

    # Exceção controlada para OpenAlex:
    # mantém apenas registros bibliograficamente fortes.
    if "openalex" in base:
        titulo_ok, _ = titulo_informativo(titulo)

        if (
            titulo_ok
            and doi
            and len(autores) >= 5
            and len(revista) >= 3
        ):
            artigo["Qualidade_OpenAlex"] = (
                "Título científico + DOI + autores + periódico"
            )
            return True, ""

    return False, "sem resumo ou palavras-chave suficientes"



def fonte_confiavel(artigo):
    revista = texto_normalizado(
        campo(artigo, "Revista", "revista", "journal", "fonte", "venue")
    )

    titulo = texto_normalizado(
        campo(artigo, "Titulo", "Título", "titulo", "title")
    )

    combinado = f"{revista} {titulo}"

    if any(p in combinado for p in PADROES_SUSPEITOS):
        return False, "fonte editorial/suspeita"

    return True, ""


def filtrar_artigos_confiaveis(artigos):
    confiaveis = []
    descartados = []

    for artigo in artigos or []:
        if not isinstance(artigo, dict):
            continue

        motivos = []

        titulo = campo(artigo, "Titulo", "Título", "titulo", "title")

        ok_titulo, motivo = titulo_informativo(titulo)
        if not ok_titulo:
            motivos.append(motivo)

        ok_conteudo, motivo = conteudo_suficiente(artigo)
        if not ok_conteudo:
            motivos.append(motivo)

        ok_fonte, motivo = fonte_confiavel(artigo)
        if not ok_fonte:
            motivos.append(motivo)

        if motivos:
            artigo["Status_Qualidade"] = "Descartado"
            artigo["Motivo_Descarte"] = "; ".join(sorted(set(motivos)))
            descartados.append(artigo)
        else:
            artigo["Status_Qualidade"] = "Aprovado"
            artigo["Motivo_Descarte"] = ""
            confiaveis.append(artigo)

    print("\nATHENA PRISMA — FILTRO DE QUALIDADE")
    print(f"Registros recebidos: {len(artigos or [])}")
    print(f"Registros confiáveis: {len(confiaveis)}")
    print(f"Registros descartados: {len(descartados)}")

    por_base = Counter(
        str(campo(a, "Base", "base") or "Não informado")
        for a in confiaveis
    )
    print(f"Confiáveis por base: {dict(por_base)}")

    motivos = Counter(
        m
        for a in descartados
        for m in str(a.get("Motivo_Descarte", "")).split("; ")
        if m
    )
    print(f"Motivos de descarte: {dict(motivos)}")

    return confiaveis, descartados

def score_completude(artigo):
    score = 0
    for campo_nome in ["Titulo", "Título", "titulo", "title"]:
        if campo(artigo, campo_nome):
            score += 3
            break
    for campo_nome in ["Resumo", "resumo", "abstract", "Abstract"]:
        if len(limpar_texto(campo(artigo, campo_nome))) >= 120:
            score += 4
            break
    for campo_nome in ["Palavras-chave", "Palavras_chave", "keywords", "Keywords", "Descritores", "descriptors"]:
        if campo(artigo, campo_nome):
            score += 2
            break
    if campo(artigo, "DOI", "doi"):
        score += 3
    if campo(artigo, "Autores", "autores", "authors", "author"):
        score += 2
    if campo(artigo, "Link", "link", "url"):
        score += 1
    if campo(artigo, "Revista", "revista", "journal", "fonte", "venue"):
        score += 1
    return score


def chave_dedup_final(artigo):
    doi = limpar_texto(campo(artigo, "DOI", "doi")).lower()
    doi = doi.replace("https://doi.org/", "").replace("http://doi.org/", "")
    doi = doi.replace("doi:", "").strip()
    if doi:
        return f"doi:{doi}"

    titulo = texto_normalizado(campo(artigo, "Titulo", "Título", "titulo", "title"))
    titulo = re.sub(r"[^a-z0-9à-ÿ ]", "", titulo)
    titulo = re.sub(r"\s+", " ", titulo).strip()
    if titulo:
        return f"titulo:{titulo}"

    link = texto_normalizado(campo(artigo, "Link", "link", "url"))
    if link:
        return f"link:{link}"

    return ""


def deduplicar_por_melhor_registro(artigos):
    """
    Deduplicação final em duas passagens:

    1. DOI normalizado, quando disponível.
    2. Título normalizado, independentemente de haver DOI.

    Em cada grupo, preserva o registro bibliograficamente mais completo.
    Artigos sem DOI não são descartados automaticamente.
    """

    prioridade_base = {
        "PubMed": 6,
        "SciELO": 6,
        "LILACS": 6,
        "OpenAlex": 5,
        "Semantic Scholar": 5,
        "Crossref": 4,
    }

    def normalizar_doi(artigo):
        doi = limpar_texto(
            campo(artigo, "DOI", "doi")
        ).lower()

        doi = doi.replace("https://doi.org/", "")
        doi = doi.replace("http://doi.org/", "")
        doi = doi.replace("http://dx.doi.org/", "")
        doi = doi.replace("doi:", "")
        doi = doi.strip().rstrip(".,;")

        return doi

    def normalizar_titulo_artigo(artigo):
        titulo = texto_normalizado(
            campo(
                artigo,
                "Titulo",
                "Título",
                "titulo",
                "title",
            )
        )

        titulo = re.sub(
            r"[^a-z0-9à-ÿ ]",
            " ",
            titulo,
        )

        titulo = re.sub(
            r"\s+",
            " ",
            titulo,
        ).strip()

        return titulo

    def pontuacao_registro(artigo):
        base = str(
            campo(artigo, "Base", "base")
            or ""
        ).strip()

        score = score_completude(artigo)
        score += prioridade_base.get(base, 2)

        autores = limpar_texto(
            campo(
                artigo,
                "Autores",
                "autores",
                "authors",
                "author",
            )
        )

        revista = limpar_texto(
            campo(
                artigo,
                "Revista",
                "revista",
                "journal",
                "fonte",
                "venue",
            )
        )

        resumo = limpar_texto(
            campo(
                artigo,
                "Resumo",
                "resumo",
                "abstract",
                "Abstract",
            )
        )

        palavras_chave = limpar_texto(
            campo(
                artigo,
                "Palavras-chave",
                "Palavras_chave",
                "PalavrasChave",
                "keywords",
                "Keywords",
                "Descritores",
                "descritores",
            )
        )

        if len(autores) >= 5:
            score += 2

        if len(revista) >= 3:
            score += 1

        if len(resumo) >= 120:
            score += 3

        if palavras_chave:
            score += 2

        if normalizar_doi(artigo):
            score += 2

        return score

    def mesclar_bases(registro_a, registro_b):
        bases = set()

        for registro in [registro_a, registro_b]:
            base = str(
                campo(registro, "Base", "base")
                or ""
            ).strip()

            if base:
                bases.add(base)

            anteriores = str(
                registro.get("Bases_Mescladas", "")
                or ""
            )

            for item in anteriores.split(";"):
                item = item.strip()
                if item:
                    bases.add(item)

        return "; ".join(sorted(bases))

    def escolher_melhor(atual, candidato):
        score_atual = pontuacao_registro(atual)
        score_candidato = pontuacao_registro(candidato)

        if score_candidato > score_atual:
            melhor = candidato
            outro = atual
        else:
            melhor = atual
            outro = candidato

        melhor["Bases_Mescladas"] = mesclar_bases(
            melhor,
            outro,
        )

        melhor["_Score_Completude"] = max(
            score_atual,
            score_candidato,
        )

        return melhor

    artigos_validos = [
        a for a in (artigos or [])
        if isinstance(a, dict)
    ]

    # ----------------------------------------------
    # PASSAGEM 1 — DEDUPLICAÇÃO POR DOI
    # ----------------------------------------------

    por_doi = {}
    sem_doi = []
    duplicatas_doi = 0

    for artigo in artigos_validos:
        doi = normalizar_doi(artigo)

        if not doi:
            sem_doi.append(artigo)
            continue

        if doi not in por_doi:
            artigo["_Score_Completude"] = (
                pontuacao_registro(artigo)
            )
            por_doi[doi] = artigo
        else:
            duplicatas_doi += 1
            por_doi[doi] = escolher_melhor(
                por_doi[doi],
                artigo,
            )

    apos_doi = list(por_doi.values()) + sem_doi

    # ----------------------------------------------
    # PASSAGEM 2 — DEDUPLICAÇÃO POR TÍTULO
    # ----------------------------------------------
    #
    # Esta passagem compara todos os registros,
    # inclusive:
    # - um com DOI versus outro sem DOI;
    # - registros com DOIs diferentes;
    # - registros recuperados de bases distintas.
    # ----------------------------------------------

    por_titulo = {}
    sem_titulo = []
    duplicatas_titulo = 0

    for artigo in apos_doi:
        titulo = normalizar_titulo_artigo(artigo)

        if not titulo:
            sem_titulo.append(artigo)
            continue

        if titulo not in por_titulo:
            artigo["_Score_Completude"] = (
                pontuacao_registro(artigo)
            )
            por_titulo[titulo] = artigo
        else:
            duplicatas_titulo += 1
            por_titulo[titulo] = escolher_melhor(
                por_titulo[titulo],
                artigo,
            )

    saida = list(por_titulo.values()) + sem_titulo

    # Campos internos não precisam aparecer no Excel.
    for artigo in saida:
        artigo.pop("_Score_Completude", None)

    print("\nATHENA PRISMA — DEDUPLICAÇÃO FINAL EM DUAS PASSAGENS")
    print(f"Registros recebidos: {len(artigos_validos)}")
    print(f"Duplicatas removidas por DOI: {duplicatas_doi}")
    print(f"Duplicatas removidas por título: {duplicatas_titulo}")
    print(f"Registros únicos finais: {len(saida)}")

    por_base = Counter(
        str(
            campo(a, "Base", "base")
            or "Não informado"
        )
        for a in saida
    )

    print(f"Registros únicos por base: {dict(por_base)}")

    sem_doi_finais = sum(
        1
        for a in saida
        if not normalizar_doi(a)
    )

    print(
        f"Registros finais sem DOI, mas mantidos por qualidade: "
        f"{sem_doi_finais}"
    )

    return saida




def auditar_descartes_openalex(
    artigos_originais,
    artigos_confiaveis,
    artigos_descartados,
    caminho="outputs/tables/auditoria_openalex_descartes.xlsx",
):
    """
    Gera auditoria separada dos registros OpenAlex.

    Não altera a seleção principal nem reinsere artigos descartados.
    O arquivo é apenas diagnóstico interno.
    """
    from pathlib import Path
    import pandas as pd

    def eh_openalex(artigo):
        base = str(
            campo(artigo, "Base", "base", "database")
            or ""
        ).strip().lower()

        return "openalex" in base

    def dados_artigo(artigo, situacao):
        titulo = limpar_texto(
            campo(
                artigo,
                "Titulo",
                "Título",
                "titulo",
                "title",
            )
        )

        autores = limpar_texto(
            campo(
                artigo,
                "Autores",
                "autores",
                "authors",
                "author",
            )
        )

        resumo = limpar_texto(
            campo(
                artigo,
                "Resumo",
                "resumo",
                "abstract",
                "Abstract",
            )
        )

        palavras_chave = limpar_texto(
            campo(
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

        return {
            "Situação": situacao,
            "Título": titulo,
            "Autores": autores,
            "Ano": campo(
                artigo,
                "Ano",
                "ano",
                "year",
            ),
            "Revista": limpar_texto(
                campo(
                    artigo,
                    "Revista",
                    "revista",
                    "journal",
                    "fonte",
                    "venue",
                )
            ),
            "DOI": limpar_texto(
                campo(
                    artigo,
                    "DOI",
                    "doi",
                )
            ),
            "Link": limpar_texto(
                campo(
                    artigo,
                    "Link",
                    "link",
                    "url",
                )
            ),
            "Tamanho do título": len(titulo),
            "Palavras no título": len(
                re.findall(
                    r"[a-zA-ZÀ-ÿ0-9]+",
                    titulo,
                )
            ),
            "Tamanho do resumo": len(resumo),
            "Quantidade de palavras-chave": len(
                re.findall(
                    r"[a-zA-ZÀ-ÿ0-9]+",
                    palavras_chave,
                )
            ),
            "Tem resumo suficiente": (
                "Sim" if len(resumo) >= 120 else "Não"
            ),
            "Tem palavras-chave suficientes": (
                "Sim"
                if len(
                    re.findall(
                        r"[a-zA-ZÀ-ÿ0-9]+",
                        palavras_chave,
                    )
                ) >= 3
                else "Não"
            ),
            "Status de qualidade": artigo.get(
                "Status_Qualidade",
                "",
            ),
            "Motivo do descarte": artigo.get(
                "Motivo_Descarte",
                "",
            ),
        }

    openalex_originais = [
        a
        for a in (artigos_originais or [])
        if isinstance(a, dict) and eh_openalex(a)
    ]

    openalex_confiaveis = [
        a
        for a in (artigos_confiaveis or [])
        if isinstance(a, dict) and eh_openalex(a)
    ]

    openalex_descartados = [
        a
        for a in (artigos_descartados or [])
        if isinstance(a, dict) and eh_openalex(a)
    ]

    linhas = []

    for artigo in openalex_confiaveis:
        linhas.append(
            dados_artigo(
                artigo,
                "Aprovado pelo filtro",
            )
        )

    for artigo in openalex_descartados:
        linhas.append(
            dados_artigo(
                artigo,
                "Descartado pelo filtro",
            )
        )

    motivos = Counter()

    for artigo in openalex_descartados:
        texto_motivos = str(
            artigo.get(
                "Motivo_Descarte",
                "",
            )
            or ""
        )

        for motivo in texto_motivos.split(";"):
            motivo = motivo.strip()

            if motivo:
                motivos[motivo] += 1

    resumo_auditoria = [
        {
            "Indicador": "OpenAlex recebidos",
            "Quantidade": len(openalex_originais),
        },
        {
            "Indicador": "OpenAlex aprovados",
            "Quantidade": len(openalex_confiaveis),
        },
        {
            "Indicador": "OpenAlex descartados",
            "Quantidade": len(openalex_descartados),
        },
    ]

    for motivo, quantidade in motivos.most_common():
        resumo_auditoria.append(
            {
                "Indicador": f"Descarte: {motivo}",
                "Quantidade": quantidade,
            }
        )

    Path(caminho).parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with pd.ExcelWriter(
        caminho,
        engine="openpyxl",
    ) as writer:
        pd.DataFrame(
            resumo_auditoria
        ).to_excel(
            writer,
            sheet_name="Resumo",
            index=False,
        )

        pd.DataFrame(
            linhas
        ).to_excel(
            writer,
            sheet_name="Registros OpenAlex",
            index=False,
        )

    print("\nATHENA PRISMA — AUDITORIA OPENALEX")
    print(
        f"OpenAlex recebidos: "
        f"{len(openalex_originais)}"
    )
    print(
        f"OpenAlex aprovados: "
        f"{len(openalex_confiaveis)}"
    )
    print(
        f"OpenAlex descartados: "
        f"{len(openalex_descartados)}"
    )
    print(
        f"Motivos de descarte: "
        f"{dict(motivos)}"
    )
    print(
        f"Arquivo de auditoria: "
        f"{caminho}"
    )

    return caminho
