import requests


def executar_busca_crossref(query, ano_inicial, ano_final, max_artigos=50):
    print("\nBuscando artigos no Crossref...")

    url = "https://api.crossref.org/works"

    params = {
        "query.bibliographic": query,
        "filter": f"from-pub-date:{ano_inicial},until-pub-date:{ano_final},type:journal-article",
        "rows": max_artigos,
        "select": "DOI,title,author,published-print,published-online,container-title,abstract,URL"
    }

    resposta = requests.get(url, params=params, timeout=30)
    resposta.raise_for_status()

    itens = resposta.json().get("message", {}).get("items", [])

    artigos = []

    for item in itens:
        titulo = item.get("title", [""])[0] if item.get("title") else ""
        revista = item.get("container-title", [""])[0] if item.get("container-title") else ""
        doi = item.get("DOI", "")
        link = item.get("URL", "")
        resumo = item.get("abstract", "")

        ano = ""
        publicado = item.get("published-print") or item.get("published-online")
        if publicado:
            partes = publicado.get("date-parts", [[]])
            if partes and partes[0]:
                ano = partes[0][0]

        autores_lista = []
        for autor in item.get("author", []):
            nome = autor.get("given", "")
            sobrenome = autor.get("family", "")
            autores_lista.append(f"{sobrenome} {nome}".strip())

        artigos.append({
            "Base": "Crossref",
            "PMID": "",
            "Titulo": titulo,
            "Autores": "; ".join(autores_lista),
            "Ano": ano,
            "Revista": revista,
            "DOI": doi,
            "Resumo": resumo,
            "Link": link
        })

    print(f"Crossref: {len(artigos)} registros encontrados.")

    return artigos