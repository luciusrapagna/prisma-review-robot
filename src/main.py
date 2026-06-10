from datetime import datetime
import os
import sys
from pathlib import Path
import pandas as pd

# Garantir que o pacote src seja importavel quando main.py for executado diretamente
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from src.buscadores.pubmed import executar_busca_pubmed
from src.buscadores.crossref import executar_busca_crossref
from src.buscadores.scielo import executar_busca_scielo
from src.buscadores.lilacs import executar_busca_lilacs

from src.prisma.duplicates import remover_duplicatas

from src.ia.ranking_semantico import (
    calcular_similaridade,
    salvar_ranking_semantico
)

from src.ia.gerador_booleano import gerar_booleano

from src.outputs.word_writer import gerar_relatorio_word


def obter_proximo_numero_projeto():
    """Determina o próximo número de projeto disponível."""
    if not os.path.exists("projetos"):
        os.makedirs("projetos", exist_ok=True)
        return 1

    projetos_existentes = []
    for item in os.listdir("projetos"):
        if os.path.isdir(os.path.join("projetos", item)) and item.startswith("projeto "):
            try:
                numero = int(item.split(" ")[1])
                projetos_existentes.append(numero)
            except (ValueError, IndexError):
                continue

    if not projetos_existentes:
        return 1

    return max(projetos_existentes) + 1


def criar_pastas_projeto(numero_projeto):
    """Cria a estrutura de pastas para o projeto específico."""
    base_projeto = f"projetos/projeto {numero_projeto}"

    pastas = [
        f"{base_projeto}/data/raw",
        f"{base_projeto}/data/processed",
        f"{base_projeto}/outputs/tables",
        f"{base_projeto}/outputs/figures",
        f"{base_projeto}/outputs/references",
        f"{base_projeto}/logs"
    ]

    for pasta in pastas:
        os.makedirs(pasta, exist_ok=True)

    return base_projeto


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

    tema = input("Digite o tema da revisao: ")
    ano_inicial = input("Ano inicial: ")
    ano_final = input("Ano final: ")

    print("\nOpcoes de busca:")
    print("1. Digitar estrategia booleana manualmente")
    print("2. Usar gerador automatico de queries booleanas")

    opcao = input("\nEscolha uma opcao (1 ou 2): ").strip()

    if opcao == "2":
        print("\nGERADOR AUTOMATICO DE QUERIES BOOLEANAS")
        print("=========================================")
        print("Digite os termos principais separados por espaco.")
        print("Exemplo: takotsubo microbiota depressao")
        print("\nTermos disponiveis com sinonimos:")
        print("- takotsubo, microbiota, depressao, ansiedade")
        print("- medicina, brasil, covid, mortalidade")
        print("- diagnostico, tratamento")

        termos_usuario = input("\nDigite os termos: ")
        query = gerar_booleano(termos_usuario)

        print(f"\nQuery booleana gerada:")
        print(query)

    else:
        print("\nExemplo de busca:")
        print('("medical education" OR "educacao medica") AND ("artificial intelligence" OR "inteligencia artificial")')

        query = input("\nDigite a estrategia de busca booleana: ")

    max_artigos = input("Numero maximo de artigos por base: ")

    if not max_artigos.strip():
        max_artigos = 50
    else:
        max_artigos = int(max_artigos)

    tipo_revisao = input("Tipo de revisao desejada: ")

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
    print("FILTRO DE SIMILARIDADE SEMANTICA")
    print("========================================")

    print("\nSugestAes:")
    print("0.40 = muito amplo")
    print("0.50 = amplo")
    print("0.60 = moderado")
    print("0.70 = rigoroso")
    print("0.80 = muito rigoroso")

    valor = input("\nDigite a similaridade mAnima desejada: ")

    if not valor.strip():
        return 0.30

    try:
        valor = float(valor.replace(",", "."))

        if valor < 0:
            print("Valor invAlido. Usando 0.30.")
            return 0.30

        if valor > 1:
            print("Valor invAlido. Usando 0.30.")
            return 0.30

        return valor

    except ValueError:
        print("Valor invAlido. Usando 0.30.")
        return 0.30


def gerar_tabela_parametros(parametros, similaridade_minima, base_projeto=""):
    dados = {
        "Campo": [
            "Tema",
            "Ano inicial",
            "Ano final",
            "Estrategia de busca",
            "Maximo de artigos por base",
            "Tipo de revisao",
            "Similaridade minima",
            "Data de execucao"
        ],
        "Informacao": [
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

    caminho = f"{base_projeto}/outputs/tables/parametros_revisao.xlsx" if base_projeto else "outputs/tables/parametros_revisao.xlsx"
    df.to_excel(caminho, index=False)

    print(f"\nTabela de parametros gerada em: {caminho}")


def salvar_tabela_consolidada(artigos, base_projeto=""):
    caminho = f"{base_projeto}/outputs/tables/tabela_consolidada_multibase.xlsx" if base_projeto else "outputs/tables/tabela_consolidada_multibase.xlsx"

    if not artigos:
        df = pd.DataFrame(columns=[
            "Base",
            "PMID",
            "Titulo",
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
    similaridade_minima,
    base_projeto=""
):
    duplicatas = total_identificados - total_sem_duplicatas
    excluidos_por_similaridade = total_sem_duplicatas - total_apos_similaridade

    texto = f"""
DescriAAo sugerida para figura PRISMA:

Fluxograma representando o processo de identificaAAo, triagem, elegibilidade e inclusAo dos estudos da revisAo intitulada "{parametros['tema']}".

A busca bibliogrAfica foi realizada nas bases PubMed, Crossref, SciELO e LILACS/BVS, considerando publicaAAes entre {parametros['ano_inicial']} e {parametros['ano_final']}.

A estratAgia de busca utilizada foi:

{parametros['query_geral']}

Na etapa de identificaAAo, foram recuperados:
- PubMed: {total_pubmed} registros;
- Crossref: {total_crossref} registros;
- SciELO: {total_scielo} registros;
- LILACS/BVS: {total_lilacs} registros.

O total inicial identificado foi de {total_identificados} registros.

ApAs a remoAAo automAtica de duplicatas, permaneceram {total_sem_duplicatas} registros Anicos. Foram removidos {duplicatas} registros duplicados.

ApAs a triagem semAntica automatizada, utilizando similaridade mAnima de {similaridade_minima}, permaneceram {total_apos_similaridade} registros. Foram excluAdos {excluidos_por_similaridade} registros por baixa similaridade com o tema da revisAo.

A figura PRISMA deverA apresentar:
1. registros identificados em cada base;
2. total de registros identificados;
3. registros removidos por duplicidade;
4. registros triados por similaridade semAntica;
5. registros excluAdos por baixa similaridade;
6. registros mantidos para leitura de tAtulo e resumo;
7. textos completos avaliados para elegibilidade;
8. textos completos excluAdos com justificativa;
9. estudos finais incluAdos na sAntese qualitativa e/ou quantitativa.

SugestAo visual:
Construir um fluxograma vertical em quatro etapas principais: IdentificaAAo, Triagem, Elegibilidade e InclusAo. Cada base de dados pode aparecer em uma caixa lateral na etapa de identificaAAo, convergindo para o total de registros identificados. Em seguida, inserir a caixa de remoAAo de duplicatas, seguida da triagem semAntica, avaliaAAo de elegibilidade e inclusAo final.

Essa descriAAo pode ser utilizada como base para criaAAo da figura no PowerPoint, Canva, CorelDRAW, BioRender ou outro software grAfico.
"""

    caminho = f"{base_projeto}/outputs/figures/descricao_figura_prisma.txt" if base_projeto else "outputs/figures/descricao_figura_prisma.txt"

    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto)

    print(f"\nDescricao da figura PRISMA gerada em: {caminho}")


def gerar_ris_zotero(artigos, base_projeto=""):
    caminho = f"{base_projeto}/outputs/references/referencias_multibase.ris" if base_projeto else "outputs/references/referencias_multibase.ris"

    with open(caminho, "w", encoding="utf-8") as arquivo:
        for artigo in artigos:
            arquivo.write("TY  - JOUR\n")
            arquivo.write(f"TI  - {artigo.get('Titulo', '')}\n")
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

    numero_projeto = obter_proximo_numero_projeto()
    base_projeto = criar_pastas_projeto(numero_projeto)

    print(f"\nPROJETO {numero_projeto} - {base_projeto}")
    print("=" * 50)

    parametros = coletar_parametros()

    similaridade_minima = perguntar_similaridade()

    gerar_tabela_parametros(
        parametros,
        similaridade_minima,
        base_projeto
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

    salvar_tabela_consolidada(todos_artigos, base_projeto)

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

    salvar_ranking_semantico(artigos_rankeados, base_projeto)

    caminho_relatorio = gerar_relatorio_word(
        parametros,
        artigos_rankeados,
        base_projeto
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
        similaridade_minima=similaridade_minima,
        base_projeto=base_projeto
    )

    gerar_ris_zotero(artigos_rankeados, base_projeto)

    print("\n========================================")
    print("ROBO EXECUTADO COM SUCESSO!")
    print("========================================")
    print(f"PubMed: {total_pubmed} registros")
    print(f"Crossref: {total_crossref} registros")
    print(f"SciELO: {total_scielo} registros")
    print(f"LILACS/BVS: {total_lilacs} registros")
    print(f"Total identificado: {total_identificados} registros")
    print(f"Total apos duplicatas: {total_sem_duplicatas} registros")
    print(f"Total apos similaridade: {total_apos_similaridade} registros")
    print(f"Similaridade minima usada: {similaridade_minima}")

    print(f"\nPROJETO SALVO EM: {base_projeto}")
    print("\nArquivos gerados em:")
    print(f"{base_projeto}/outputs/tables")
    print(f"{base_projeto}/outputs/figures")
    print(f"{base_projeto}/outputs/references")
    print(caminho_relatorio)


if __name__ == "__main__":
    main()
