import asyncio
import aiohttp
from Bio import Entrez

Entrez.email = "luciusrapagna@gmail.com"


async def buscar_crossref_async(query, ano_inicial, ano_final, max_artigos=30):
    url = "https://api.crossref.org/works"
    params = {
        "query": query,
        "filter": f"from-pub-date:{ano_inicial},until-pub-date:{ano_final}",
        "rows": max_artigos
    }

    artigos = []

    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params, timeout=30) as resp:
            data = await resp.json()

    for item in data.get("message", {}).get("items", []):
        titulo = item.get("title", [""])[0] if item.get("title") else ""
        autores = item.get("author", [])
        ano = ""
        if "published-print" in item:
            ano = item["published-print"]["date-parts"][0][0]
        elif "published-online" in item:
            ano = item["published-online"]["date-parts"][0][0]

        artigos.append({
            "base": "Crossref",
            "titulo": titulo,
            "autores": "; ".join(
                [f"{a.get('family', '')}, {a.get('given', '')}" for a in autores]
            ),
            "ano": ano,
            "doi": item.get("DOI", ""),
            "resumo": item.get("abstract", ""),
            "url": item.get("URL", "")
        })

    return artigos


def buscar_pubmed_sync(query, ano_inicial, ano_final, max_artigos=30):
    termo = f'({query}) AND ("{ano_inicial}"[Date - Publication] : "{ano_final}"[Date - Publication])'

    handle = Entrez.esearch(
        db="pubmed",
        term=termo,
        retmax=max_artigos
    )
    record = Entrez.read(handle)
    ids = record.get("IdList", [])

    if not ids:
        return []

    handle = Entrez.efetch(
        db="pubmed",
        id=",".join(ids),
        rettype="xml"
    )
    records = Entrez.read(handle)

    artigos = []

    for article in records.get("PubmedArticle", []):
        medline = article.get("MedlineCitation", {})
        art = medline.get("Article", {})

        titulo = art.get("ArticleTitle", "")
        abstract = art.get("Abstract", {}).get("AbstractText", [""])
        resumo = " ".join([str(x) for x in abstract])

        journal = art.get("Journal", {})
        ano = ""
        try:
            ano = journal["JournalIssue"]["PubDate"].get("Year", "")
        except Exception:
            ano = ""

        autores_lista = []
        for autor in art.get("AuthorList", []):
            sobrenome = autor.get("LastName", "")
            nome = autor.get("ForeName", "")
            autores_lista.append(f"{sobrenome}, {nome}".strip(", "))

        artigos.append({
            "base": "PubMed",
            "titulo": str(titulo),
            "autores": "; ".join(autores_lista),
            "ano": ano,
            "doi": "",
            "resumo": resumo,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{medline.get('PMID', '')}/"
        })

    return artigos


async def executar_busca_async(query, ano_inicial, ano_final, max_artigos=30):
    loop = asyncio.get_event_loop()

    pubmed_task = loop.run_in_executor(
        None,
        buscar_pubmed_sync,
        query,
        ano_inicial,
        ano_final,
        max_artigos
    )

    crossref_task = buscar_crossref_async(
        query,
        ano_inicial,
        ano_final,
        max_artigos
    )

    pubmed, crossref = await asyncio.gather(pubmed_task, crossref_task)

    return pubmed + crossref
