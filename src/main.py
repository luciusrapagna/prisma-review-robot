from datetime import datetime
import os
import pandas as pd

from buscadores.pubmed import executar_busca_pubmed


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
    print("       PRISMA REVIEW ROBOT")
    print("========================================\n")

    tema = input("Digite o tema da revisão: ")
    ano_inicial = input("Ano inicial: ")
    ano_final = input("Ano final: ")

    print("\nExemplo de busca PubMed:")
    print('("medical education"[Title/Abstract]) AND ("artificial intelligence"[Title/Abstract])')

    query_pubmed = input("\nDigite a busca booleana para o PubMed: ")

    max_artigos = input("Número máximo de artigos no PubMed: ")

    if not max_artigos.strip():
        max_artigos = 50
    else:
        max_artigos = int(max_artigos)

    tipo_revisao = input("Tipo de revisão desejada: ")

    parametros = {
        "tema": tema,
        "ano_inicial": ano_inicial,
        "ano_final": ano_final,
        "query_pubmed": query_pubmed,
        "max_artigos": max_artigos,
        "tipo_revisao": tipo_revisao,
        "data_execucao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return parametros


def gerar_tabela_parametros(parametros):
    dados = {
        "Campo": [
            "Tema",
            "Ano inicial",
            "Ano final",
            "Busca PubMed",
            "Máximo de artigos",
            "Tipo de revisão",
            "Data de execução"
        ],
        "Informação": [
            parametros["tema"],
            parametros["ano_inicial"],
            parametros["ano_final"],
            parametros["query_pubmed"],
            parametros["max_artigos"],
            parametros["tipo_revisao"],
            parametros["data_execucao"]
        ]
    }

    df = pd.DataFrame(dados)

    caminho = "outputs/tables/parametros_revisao.xlsx"
    df.to_excel(caminho, index=False)

    print(f"\nTabela de parâmetros gerada em: {caminho}")


def gerar_descricao_figura_prisma(parametros, total_pubmed):
    texto = f"""
Descrição sugerida para figura PRISMA:

Fluxograma representando o processo de identificação, triagem, elegibilidade e inclusão dos estudos da revisão intitulada "{parametros['tema']}".

A busca bibliográfica foi realizada no PubMed, considerando publicações entre {parametros['ano_inicial']} e {parametros['ano_final']}.

A estratégia de busca utilizada foi:

{parametros['query_pubmed']}

Na etapa de identificação, foram recuperados {total_pubmed} registros no PubMed.

A figura deverá apresentar:
1. registros identificados nas bases consultadas;
2. registros removidos por duplicidade;
3. estudos triados por título e resumo;
4. estudos excluídos após triagem;
5. textos completos avaliados para elegibilidade;
6. estudos excluídos com justificativa;
7. estudos finais incluídos na síntese qualitativa e/ou quantitativa.

Essa descrição poderá ser usada como base para construção de um fluxograma PRISMA em CorelDRAW, PowerPoint, Canva, BioRender ou outro software gráfico.
"""

    caminho = "outputs/figures/descricao_figura_prisma.txt"

    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto)

    print(f"Descrição da figura PRISMA gerada em: {caminho}")


def gerar_ris_zotero(artigos):
    caminho = "outputs/references/referencias_pubmed.ris"

    with open(caminho, "w", encoding="utf-8") as arquivo:
        for artigo in artigos:
            arquivo.write("TY  - JOUR\n")
            arquivo.write(f"TI  - {artigo.get('Título', '')}\n")
            arquivo.write(f"PY  - {artigo.get('Ano', '')}\n")
            arquivo.write(f"JO  - {artigo.get('Revista', '')}\n")
            arquivo.write(f"DO  - {artigo.get('DOI', '')}\n")
            arquivo.write(f"UR  - {artigo.get('Link', '')}\n")

            autores = artigo.get("Autores", "")
            if autores:
                for autor in autores.split("; "):
                    arquivo.write(f"AU  - {autor}\n")

            arquivo.write("ER  -\n\n")

    print(f"Arquivo RIS para Zotero gerado em: {caminho}")


def main():
    criar_pastas()

    parametros = coletar_parametros()

    gerar_tabela_parametros(parametros)

    artigos_pubmed = executar_busca_pubmed(
        query=parametros["query_pubmed"],
        ano_inicial=parametros["ano_inicial"],
        ano_final=parametros["ano_final"],
        max_artigos=parametros["max_artigos"],
        tema=parametros["tema"]
    )

    gerar_descricao_figura_prisma(
        parametros=parametros,
        total_pubmed=len(artigos_pubmed)
    )

    gerar_ris_zotero(artigos_pubmed)

    print("\nRobô executado com sucesso!")
    print("Verifique as pastas outputs/tables, outputs/figures e outputs/references.")


if __name__ == "__main__":
    main()