import requests


def executar_busca_lilacs(query, ano_inicial, ano_final, max_artigos=50):
    print("\nBuscando artigos na LILACS/BVS...")

    url = "https://pesquisa.bvsalud.org/portal/"

    params = {
        "q": query,
        "lang": "pt",
        "count": max_artigos,
        "output": "json",
        "filter": "db:LILACS"
    }

    try:
        resposta = requests.get(url, params=params, timeout=30)
        resposta.raise_for_status()
        dados = resposta.json()
    except Exception as erro:
        print(f"Aviso: nao foi possivel consultar LILACS/BVS automaticamente: {erro}")
        return []

    resultados = dados.get("results", []) or dados.get("items", [])

    artigos = []

    for item in resultados:
        titulo = item.get("title", "") or item.get("ti", "")
        autores = item.get("authors", "") or item.get("au", "")
        ano = item.get("year", "") or item.get("publication_year", "")
        revista = item.get("journal", "") or item.get("source", "")
        doi = item.get("doi", "")
        resumo = item.get("abstract", "") or item.get("ab", "")
        link = item.get("url", "") or item.get("link", "")

        try:
            ano_int = int(str(ano)[:4])
            if ano_int < int(ano_inicial) or ano_int > int(ano_final):
                continue
        except Exception:
            pass

        artigos.append({
            "Base": "LILACS",
            "PMID": "",
            "Titulo": titulo,
            "Autores": autores if isinstance(autores, str) else "; ".join(autores),
            "Ano": ano,
            "Revista": revista,
            "DOI": doi,
            "Resumo": resumo,
            "Link": link
        })

    print(f"LILACS: {len(artigos)} registros encontrados.")

    return artigos