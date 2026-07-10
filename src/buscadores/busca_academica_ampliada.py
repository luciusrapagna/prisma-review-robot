import requests
from urllib.parse import quote_plus


def _limpar_doi(doi):
    if not doi:
        return ""
    doi = str(doi).strip()
    doi = doi.replace("https://doi.org/", "").replace("http://dx.doi.org/", "")
    return doi


def _reconstruir_abstract_openalex(indice):
    """
    Reconstrói o resumo do OpenAlex a partir de abstract_inverted_index.
    """
    if not isinstance(indice, dict) or not indice:
        return ""

    posicoes = []

    for palavra, indices in indice.items():
        if not isinstance(indices, list):
            continue

        for posicao in indices:
            try:
                posicoes.append((int(posicao), str(palavra)))
            except Exception:
                continue

    if not posicoes:
        return ""

    posicoes.sort(key=lambda x: x[0])

    return " ".join(
        palavra
        for _, palavra in posicoes
    ).strip()


def _extrair_keywords_openalex(item):
    """
    Usa keywords e conceitos do OpenAlex como descritores internos.
    """
    termos = []

    for keyword in item.get("keywords") or []:
        if isinstance(keyword, dict):
            nome = (
                keyword.get("display_name")
                or keyword.get("keyword")
            )
        else:
            nome = str(keyword)

        if nome:
            termos.append(str(nome).strip())

    for conceito in item.get("concepts") or []:
        if not isinstance(conceito, dict):
            continue

        nome = conceito.get("display_name")
        score = conceito.get("score", 0)

        try:
            score = float(score)
        except Exception:
            score = 0

        if nome and score >= 0.30:
            termos.append(str(nome).strip())

    unicos = []
    vistos = set()

    for termo in termos:
        chave = termo.lower()

        if chave and chave not in vistos:
            vistos.add(chave)
            unicos.append(termo)

    return "; ".join(unicos[:15])


def buscar_openalex(query, ano_inicial=None, ano_final=None, max_artigos=50):
    url = "https://api.openalex.org/works"

    filtro = []

    if ano_inicial:
        filtro.append(
            f"from_publication_date:{ano_inicial}-01-01"
        )

    if ano_final:
        filtro.append(
            f"to_publication_date:{ano_final}-12-31"
        )

    params = {
        "search": query,
        "per-page": min(int(max_artigos), 200),
        "select": (
            "id,title,doi,publication_year,"
            "authorships,locations,primary_location,"
            "abstract_inverted_index,keywords,concepts,type"
        ),
    }

    if filtro:
        params["filter"] = ",".join(filtro)

    headers = {
        "User-Agent": (
            "ATHENA-PRISMA/1.0 "
            "(mailto:contato@athenascientific.com)"
        )
    }

    try:
        r = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=45,
        )
        r.raise_for_status()
        dados = r.json()

    except Exception as e:
        print(f"Aviso: falha no OpenAlex: {e}")
        return []

    artigos = []

    for item in dados.get("results", []):
        titulo = item.get("title") or ""

        if not titulo:
            continue

        doi = _limpar_doi(
            item.get("doi") or ""
        )

        ano = item.get("publication_year") or ""

        autores = []

        for aut in item.get("authorships") or []:
            nome = (
                aut.get("author", {})
                .get("display_name")
            )

            if nome:
                autores.append(nome)

        revista = ""

        primary_location = (
            item.get("primary_location")
            or {}
        )

        source = (
            primary_location.get("source")
            or {}
        )

        revista = (
            source.get("display_name")
            or ""
        )

        if not revista:
            locations = item.get("locations") or []

            for location in locations:
                source = (
                    (location or {}).get("source")
                    or {}
                )

                revista = (
                    source.get("display_name")
                    or ""
                )

                if revista:
                    break

        resumo = _reconstruir_abstract_openalex(
            item.get("abstract_inverted_index")
        )

        palavras_chave = _extrair_keywords_openalex(
            item
        )

        link = (
            item.get("doi")
            or item.get("id")
            or ""
        )

        artigos.append({
            "Base": "OpenAlex",
            "PMID": "",
            "Titulo": titulo,
            "Autores": "; ".join(autores),
            "Ano": ano,
            "Revista": revista,
            "DOI": doi,
            "Resumo": resumo,
            "Palavras-chave": palavras_chave,
            "Link": link,
            "Tipo_Documento": item.get("type") or "",
        })

    com_resumo = sum(
        1 for a in artigos
        if str(a.get("Resumo") or "").strip()
    )

    com_keywords = sum(
        1 for a in artigos
        if str(a.get("Palavras-chave") or "").strip()
    )

    print(
        f"OpenAlex: {len(artigos)} registros | "
        f"com resumo={com_resumo} | "
        f"com palavras-chave={com_keywords}"
    )

    return artigos



def buscar_semantic_scholar(query, ano_inicial=None, ano_final=None, max_artigos=50):
    url = "https://api.semanticscholar.org/graph/v1/paper/search"

    fields = "title,authors,year,venue,externalIds,url,abstract"

    params = {
        "query": query,
        "limit": min(int(max_artigos), 100),
        "fields": fields,
    }

    if ano_inicial or ano_final:
        inicio = ano_inicial or ""
        fim = ano_final or ""
        params["year"] = f"{inicio}-{fim}"

    try:
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        dados = r.json()
    except Exception as e:
        print(f"Aviso: falha no Semantic Scholar: {e}")
        return []

    artigos = []

    for item in dados.get("data", []):
        titulo = item.get("title") or ""
        externos = item.get("externalIds") or {}
        doi = _limpar_doi(externos.get("DOI") or "")
        autores = "; ".join([a.get("name", "") for a in item.get("authors", []) if a.get("name")])

        if not titulo:
            continue

        artigos.append({
            "Base": "Semantic Scholar",
            "PMID": externos.get("PubMed", "") or "",
            "Titulo": titulo,
            "Autores": autores,
            "Ano": item.get("year") or "",
            "Revista": item.get("venue") or "",
            "DOI": doi,
            "Resumo": item.get("abstract") or "",
            "Link": item.get("url") or "",
        })

    return artigos


def executar_busca_academica_ampliada(
    query,
    ano_inicial=None,
    ano_final=None,
    max_artigos=50,
    query_ingles=None,
):
    print("\nBuscando referências na Busca Acadêmica Ampliada...")
    print("Fontes: OpenAlex + Semantic Scholar")
    print(f"Query original: {query}")

    def traduzir_termos_basicos(q):
        mapa = {
            "sistema único de saúde": "Brazilian Unified Health System",
            "atenção primária": "primary care",
            "atenção básica": "primary care",
            "educação médica": "medical education",
            "estudantes de medicina": "medical students",
            "acadêmicos de medicina": "medical students",
            "alunos de medicina": "medical students",
            "percepção": "perception",
            "conhecimento": "knowledge",
            "atitude": "attitude",
            "prática": "practice",
            "entrevista": "interview",
            "entrevistas": "interviews",
            "saúde pública": "public health",
            "saúde coletiva": "collective health",
            "currículo": "curriculum",
            "ensino": "teaching",
            "aprendizagem": "learning",
            "formação médica": "medical training",
            "medicina": "medicine",
            "médicos": "physicians",
            "profissionais de saúde": "health professionals",
            "revisão sistemática": "systematic review",
            "revisão integrativa": "integrative review",
            "bibliométrico": "bibliometric",
            "qualitativo": "qualitative",
            "quantitativo": "quantitative",
        }

        saida = str(q or "")
        for pt, en in mapa.items():
            saida = saida.replace(pt, en)
            saida = saida.replace(pt.capitalize(), en)
        return saida

    queries = []

    if query and str(query).strip():
        queries.append(("Português/Original", str(query).strip()))

    query_traduzida = traduzir_termos_basicos(query)

    if query_ingles and str(query_ingles).strip():
        query_traduzida = traduzir_termos_basicos(query_ingles)

    if query_traduzida and query_traduzida.strip() != str(query).strip():
        queries.append(("Inglês/Expandida", query_traduzida.strip()))

    todos_artigos = []
    vistos = set()

    for idioma, query_atual in queries:
        print(f"\nExecutando estratégia {idioma}: {query_atual}")

        artigos_openalex = buscar_openalex(
            query=query_atual,
            ano_inicial=ano_inicial,
            ano_final=ano_final,
            max_artigos=max_artigos,
        )

        artigos_semantic = buscar_semantic_scholar(
            query=query_atual,
            ano_inicial=ano_inicial,
            ano_final=ano_final,
            max_artigos=max_artigos,
        )

        print(
            f"{idioma}: OpenAlex={len(artigos_openalex)} | "
            f"Semantic Scholar={len(artigos_semantic)}"
        )

        for artigo in artigos_openalex + artigos_semantic:
            doi = str(artigo.get("DOI") or "").strip().lower()
            titulo = str(artigo.get("Titulo") or "").strip().lower()

            chave = doi if doi else titulo

            if not chave:
                continue

            if chave not in vistos:
                vistos.add(chave)
                artigo["EstrategiaBusca"] = idioma
                todos_artigos.append(artigo)

    com_doi = [
        a for a in todos_artigos
        if str(a.get("DOI") or "").strip()
    ]

    print(
        f"\nBusca Acadêmica Ampliada: "
        f"{len(todos_artigos)} registros únicos encontrados."
    )
    print(
        f"Busca Acadêmica Ampliada: "
        f"{len(com_doi)} registros com DOI."
    )

    return todos_artigos

