import requests
import xml.etree.ElementTree as ET
import pandas as pd
from datetime import datetime
from pathlib import Path


BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def buscar_pmids_pubmed(query, ano_inicial, ano_final, max_artigos=50):
    url = f"{BASE_URL}/esearch.fcgi"

    parametros = {
        "db": "pubmed",
        "term": query,
        "retmax": max_artigos,
        "retmode": "json",
        "mindate": ano_inicial,
        "maxdate": ano_final,
        "datetype": "pdat"
    }

    resposta = requests.get(url, params=parametros, timeout=30)
    resposta.raise_for_status()

    dados = resposta.json()
    pmids = dados.get("esearchresult", {}).get("idlist", [])

    return pmids


def baixar_detalhes_pubmed(pmids):
    if not pmids:
        return []

    url = f"{BASE_URL}/efetch.fcgi"

    parametros = {
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml"
    }

    resposta = requests.get(url, params=parametros, timeout=30)
    resposta.raise_for_status()

    raiz = ET.fromstring(resposta.content)

    artigos = []

    for artigo in raiz.findall(".//PubmedArticle"):
        medline = artigo.find("MedlineCitation")
        article = medline.find("Article") if medline is not None else None

        pmid = medline.findtext("PMID") if medline is not None else ""

        titulo = article.findtext("ArticleTitle") if article is not None else ""

        abstract_partes = []
        if article is not None:
            for parte in article.findall(".//AbstractText"):
                if parte.text:
                    abstract_partes.append(parte.text)

        resumo = " ".join(abstract_partes)

        journal = ""
        ano = ""

        if article is not None:
            journal = article.findtext(".//Journal/Title") or ""

            pub_date = article.find(".//JournalIssue/PubDate")
            if pub_date is not None:
                ano = pub_date.findtext("Year") or pub_date.findtext("MedlineDate") or ""

        autores_lista = []
        if article is not None:
            for autor in article.findall(".//Author"):
                sobrenome = autor.findtext("LastName")
                iniciais = autor.findtext("Initials")

                if sobrenome:
                    if iniciais:
                        autores_lista.append(f"{sobrenome} {iniciais}")
                    else:
                        autores_lista.append(sobrenome)

        autores = "; ".join(autores_lista)

        doi = ""
        for id_artigo in artigo.findall(".//ArticleId"):
            if id_artigo.attrib.get("IdType") == "doi":
                doi = id_artigo.text or ""

        link = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else ""

        artigos.append({
            "Base": "PubMed",
            "PMID": pmid,
            "Título": titulo,
            "Autores": autores,
            "Ano": ano,
            "Revista": journal,
            "DOI": doi,
            "Resumo": resumo,
            "Link": link
        })

    return artigos


def salvar_resultados_pubmed(artigos, tema):
    data_execucao = datetime.now().strftime("%Y%m%d_%H%M%S")

    nome_limpo = (
        tema.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace(":", "_")
    )

    pasta_saida = Path("outputs") / "tables"
    pasta_saida.mkdir(parents=True, exist_ok=True)

    caminho_excel = pasta_saida / f"pubmed_{nome_limpo}_{data_execucao}.xlsx"

    df = pd.DataFrame(artigos)
    df.to_excel(caminho_excel, index=False)

    return caminho_excel


def executar_busca_pubmed(query, ano_inicial, ano_final, max_artigos, tema):
    print("\nBuscando artigos no PubMed...")

    pmids = buscar_pmids_pubmed(
        query=query,
        ano_inicial=ano_inicial,
        ano_final=ano_final,
        max_artigos=max_artigos
    )

    print(f"PMIDs encontrados: {len(pmids)}")

    artigos = baixar_detalhes_pubmed(pmids)

    caminho_excel = salvar_resultados_pubmed(artigos, tema)

    print(f"Planilha PubMed gerada em: {caminho_excel}")

    return artigos