from datetime import datetime
import os
import pandas as pd

from buscadores.pubmed import executar_busca_pubmed
from buscadores.crossref import executar_busca_crossref
from buscadores.scielo import executar_busca_scielo
from buscadores.lilacs import executar_busca_lilacs

from prisma.duplicates import remover_duplicatas

from ia.ranking_semantico import (
    calcular_similaridade,
    salvar_ranking_semantico
)

from outputs.word_writer import gerar_relatorio_word


def criar_pastas():
    pastas = [
        "data/raw",
        "data/processed",
        "outputs/tables",
        "outputs/figures",
        "outputs/references",
        "logs"
    ]

    for pasta in pastas:
        os.makedirs(pasta, exist_ok=True)


def coletar_parametros():
    print("\n========================================")
    print("        PRISMA REVIEW ROBOT")
    print("========================================\n")

    tema = input("Digite o tema da revisÃ£o: ")
    ano_inicial = input("Ano inicial: ")
    ano_final = input("Ano final: ")

    print("\nExemplo de busca:")
    print('("medical education" OR "educaÃ§Ã£o mÃ©dica") AND ("artificial intelligence" OR "inteligÃªncia artificial")')

    query = input("\nDigite a estratÃ©gia de busca booleana: ")

    max_artigos = input("NÃºmero mÃ¡ximo de artigos por base: ")

    if not max_artigos.strip():
        max_artigos = 50
    else:
        max_artigos = int(max_artigos)

    tipo_revisao = input("Tipo de revisÃ£o desejada: ")

    parametros = {
        "tema": tema,
        "ano_inicial": ano_inicial,
        "ano_final": ano_final,
        "query_pubmed": query,
        "query_geral": query,
        "max_artigos": max_artigos,
        "tipo_revisao": tipo_revisao,
        "data_execucao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return parametros


def perguntar_similaridade():
    print("\n========================================")
    print("FILTRO DE SIMILARIDADE SEMÃ‚NTICA")
    print("========================================")

    print("\nSugestÃµes:")
    print("0.40 = muito amplo")
    print("0.50 = amplo")
    print("0.60 = moderado")
    print("0.70 = rigoroso")
    print("0.80 = muito rigoroso")

    valor = input("\nDigite a similaridade mÃ­nima desejada: ")

    if not valor.strip():
        return 0.30

    try:
        valor = float(valor.replace(",", "."))

        if valor < 0:
            print("Valor invÃ¡lido. Usando 0.30.")
            return 0.30

        if valor > 1:
            print("Valor invÃ¡lido. Usando 0.30.")
            return 0.30

        return valor

    except ValueError:
        print("Valor invÃ¡lido. Usando 0.30.")
        return 0.30


def gerar_tabela_parametros(parametros, similaridade_minima):
    dados = {
        "Campo": [
            "Tema",
            "Ano inicial",
            "Ano final",
            "EstratÃ©gia de busca",
            "MÃ¡ximo de artigos por base",
            "Tipo de revisÃ£o",
            "Similaridade mÃ­nima",
            "Data de execuÃ§Ã£o"
        ],
        "InformaÃ§Ã£o": [
            parametros["tema"],
            parametros["ano_inicial"],
            parametros["ano_final"],
            parametros["query_geral"],
            parametros["max_artigos"],
            parametros["tipo_revisao"],
            similaridade_minima,
            parametros["data_execucao"]
        ]
    }

    df = pd.DataFrame(dados)

    caminho = "outputs/tables/parametros_revisao.xlsx"
    df.to_excel(caminho, index=False)

    print(f"\nTabela de parÃ¢metros gerada em: {caminho}")


def salvar_tabela_consolidada(artigos):
    caminho = "outputs/tables/tabela_consolidada_multibase.xlsx"

    if not artigos:
        df = pd.DataFrame(columns=[
            "Base",
            "PMID",
            "TÃ­tulo",
            "Autores",
            "Ano",
            "Revista",
            "DOI",
            "Resumo",
            "Link"
        ])
    else:
        df = pd.DataFrame(artigos)

    df.to_excel(caminho, index=False)

    print(f"\nTabela consolidada multibase salva em: {caminho}")


def gerar_descricao_figura_prisma(
    parametros,
    total_pubmed,
    total_crossref,
    total_scielo,
    total_lilacs,
    total_identificados,
    total_sem_duplicatas,
    total_apos_similaridade,
    similaridade_minima
):
    duplicatas = total_identificados - total_sem_duplicatas
    excluidos_por_similaridade = total_sem_duplicatas - total_apos_similaridade

    texto = f"""
DescriÃ§Ã£o sugerida para figura PRISMA:

Fluxograma representando o processo de identificaÃ§Ã£o, triagem, elegibilidade e inclusÃ£o dos estudos da revisÃ£o intitulada "{parametros['tema']}".

A busca bibliogrÃ¡fica foi realizada nas bases PubMed, Crossref, SciELO e LILACS/BVS, considerando publicaÃ§Ãµes entre {parametros['ano_inicial']} e {parametros['ano_final']}.

A estratÃ©gia de busca utilizada foi:

{parametros['query_geral']}

Na etapa de identificaÃ§Ã£o, foram recuperados:
- PubMed: {total_pubmed} registros;
- Crossref: {total_crossref} registros;
- SciELO: {total_scielo} registros;
- LILACS/BVS: {total_lilacs} registros.

O total inicial identificado foi de {total_identificados} registros.

ApÃ³s a remoÃ§Ã£o automÃ¡tica de duplicatas, permaneceram {total_sem_duplicatas} registros Ãºnicos. Foram removidos {duplicatas} registros duplicados.

ApÃ³s a triagem semÃ¢ntica automatizada, utilizando similaridade mÃ­nima de {similaridade_minima}, permaneceram {total_apos_similaridade} registros. Foram excluÃ­dos {excluidos_por_similaridade} registros por baixa similaridade com o tema da revisÃ£o.

A figura PRISMA deverÃ¡ apresentar:
1. registros identificados em cada base;
2. total de registros identificados;
3. registros removidos por duplicidade;
4. registros triados por similaridade semÃ¢ntica;
5. registros excluÃ­dos por baixa similaridade;
6. registros mantidos para leitura de tÃ­tulo e resumo;
7. textos completos avaliados para elegibilidade;
8. textos completos excluÃ­dos com justificativa;
9. estudos finais incluÃ­dos na sÃ­ntese qualitativa e/ou quantitativa.

SugestÃ£o visual:
Construir um fluxograma vertical em quatro etapas principais: IdentificaÃ§Ã£o, Triagem, Elegibilidade e InclusÃ£o. Cada base de dados pode aparecer em uma caixa lateral na etapa de identificaÃ§Ã£o, convergindo para o total de registros identificados. Em seguida, inserir a caixa de remoÃ§Ã£o de duplicatas, seguida da triagem semÃ¢ntica, avaliaÃ§Ã£o de elegibilidade e inclusÃ£o final.

Essa descriÃ§Ã£o pode ser utilizada como base para criaÃ§Ã£o da figura no PowerPoint, Canva, CorelDRAW, BioRender ou outro software grÃ¡fico.
"""

    caminho = "outputs/figures/descricao_figura_prisma.txt"

    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto)

    print(f"\nDescriÃ§Ã£o da figura PRISMA gerada em: {caminho}")


def gerar_ris_zotero(artigos):
    caminho = "outputs/references/referencias_multibase.ris"

    with open(caminho, "w", encoding="utf-8") as arquivo:
        for artigo in artigos:
            arquivo.write("TY  - JOUR\n")
            arquivo.write(f"TI  - {artigo.get('TÃ­tulo', '')}\n")
            arquivo.write(f"PY  - {artigo.get('Ano', '')}\n")
            arquivo.write(f"JO  - {artigo.get('Revista', '')}\n")
            arquivo.write(f"DO  - {artigo.get('DOI', '')}\n")
            arquivo.write(f"UR  - {artigo.get('Link', '')}\n")

            autores = artigo.get("Autores", "")
            if autores:
                if isinstance(autores, list):
                    for autor in autores:
                        arquivo.write(f"AU  - {autor}\n")
                else:
                    for autor in str(autores).split("; "):
                        if autor.strip():
                            arquivo.write(f"AU  - {autor.strip()}\n")

            arquivo.write("ER  -\n\n")

    print(f"\nArquivo RIS para Zotero gerado em: {caminho}")


def executar_buscas(parametros):
    artigos_pubmed = executar_busca_pubmed(
        query=parametros["query_pubmed"],
        ano_inicial=parametros["ano_inicial"],
        ano_final=parametros["ano_final"],
        max_artigos=parametros["max_artigos"],
        tema=parametros["tema"]
    )

    artigos_crossref = executar_busca_crossref(
        query=parametros["query_geral"],
        ano_inicial=parametros["ano_inicial"],
        ano_final=parametros["ano_final"],
        max_artigos=parametros["max_artigos"]
    )

    artigos_scielo = executar_busca_scielo(
        query=parametros["query_geral"],
        ano_inicial=parametros["ano_inicial"],
        ano_final=parametros["ano_final"],
        max_artigos=parametros["max_artigos"]
    )

    artigos_lilacs = executar_busca_lilacs(
        query=parametros["query_geral"],
        ano_inicial=parametros["ano_inicial"],
        ano_final=parametros["ano_final"],
        max_artigos=parametros["max_artigos"]
    )

    return artigos_pubmed, artigos_crossref, artigos_scielo, artigos_lilacs


def main():
    criar_pastas()

    parametros = coletar_parametros()

    similaridade_minima = perguntar_similaridade()

    gerar_tabela_parametros(
        parametros,
        similaridade_minima
    )

    (
        artigos_pubmed,
        artigos_crossref,
        artigos_scielo,
        artigos_lilacs
    ) = executar_buscas(parametros)

    todos_artigos = (
        artigos_pubmed
        + artigos_crossref
        + artigos_scielo
        + artigos_lilacs
    )

    salvar_tabela_consolidada(todos_artigos)

    total_pubmed = len(artigos_pubmed)
    total_crossref = len(artigos_crossref)
    total_scielo = len(artigos_scielo)
    total_lilacs = len(artigos_lilacs)
    total_identificados = len(todos_artigos)

    artigos_sem_duplicatas = remover_duplicatas(todos_artigos)

    total_sem_duplicatas = len(artigos_sem_duplicatas)

    artigos_rankeados = calcular_similaridade(
        tema=parametros["tema"],
        artigos=artigos_sem_duplicatas,
        similaridade_minima=similaridade_minima
    )

    total_apos_similaridade = len(artigos_rankeados)

    salvar_ranking_semantico(artigos_rankeados)

    caminho_relatorio = gerar_relatorio_word(
        parametros,
        artigos_rankeados
    )

    gerar_descricao_figura_prisma(
        parametros=parametros,
        total_pubmed=total_pubmed,
        total_crossref=total_crossref,
        total_scielo=total_scielo,
        total_lilacs=total_lilacs,
        total_identificados=total_identificados,
        total_sem_duplicatas=total_sem_duplicatas,
        total_apos_similaridade=total_apos_similaridade,
        similaridade_minima=similaridade_minima
    )

    gerar_ris_zotero(artigos_rankeados)

    print("\n========================================")
    print("ROBÃ” EXECUTADO COM SUCESSO!")
    print("========================================")
    print(f"PubMed: {total_pubmed} registros")
    print(f"Crossref: {total_crossref} registros")
    print(f"SciELO: {total_scielo} registros")
    print(f"LILACS/BVS: {total_lilacs} registros")
    print(f"Total identificado: {total_identificados} registros")
    print(f"Total apÃ³s duplicatas: {total_sem_duplicatas} registros")
    print(f"Total apÃ³s similaridade: {total_apos_similaridade} registros")
    print(f"Similaridade mÃ­nima usada: {similaridade_minima}")

    print("\nArquivos gerados em:")
    print("outputs/tables")
    print("outputs/figures")
    print("outputs/references")
    print(caminho_relatorio)


if __name__ == "__main__":
    main()
