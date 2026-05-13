from datetime import datetime
import os
import pandas as pd


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
    descritores = input("Digite os descritores separados por vírgula: ")
    tipo_revisao = input("Tipo de revisão desejada: ")

    parametros = {
        "tema": tema,
        "ano_inicial": ano_inicial,
        "ano_final": ano_final,
        "descritores": descritores,
        "tipo_revisao": tipo_revisao,
        "data_execucao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    return parametros


def gerar_tabela_inicial(parametros):

    dados = {
        "Campo": [
            "Tema",
            "Ano inicial",
            "Ano final",
            "Descritores",
            "Tipo de revisão",
            "Data de execução"
        ],
        "Informação": [
            parametros["tema"],
            parametros["ano_inicial"],
            parametros["ano_final"],
            parametros["descritores"],
            parametros["tipo_revisao"],
            parametros["data_execucao"]
        ]
    }

    df = pd.DataFrame(dados)

    caminho = "outputs/tables/parametros_revisao.xlsx"

    df.to_excel(caminho, index=False)

    print(f"\nTabela inicial gerada em: {caminho}")


def gerar_descricao_figura_prisma(parametros):

    texto = f"""
Descrição sugerida para figura PRISMA:

Fluxograma representando o processo de identificação, triagem, elegibilidade e inclusão dos estudos na revisão intitulada "{parametros['tema']}".

A busca bibliográfica considerou publicações entre {parametros['ano_inicial']} e {parametros['ano_final']}, utilizando os seguintes descritores: {parametros['descritores']}.

A figura deverá apresentar o número total de registros identificados nas bases consultadas, os registros removidos por duplicidade, os estudos excluídos após leitura de título e resumo, os textos completos avaliados para elegibilidade e os estudos finais incluídos na síntese qualitativa e/ou quantitativa.
"""

    caminho = "outputs/figures/descricao_figura_prisma.txt"

    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto)

    print(f"Descrição da figura PRISMA gerada em: {caminho}")


def gerar_referencia_zotero_exemplo():

    conteudo = """TY  - JOUR
TI  - Exemplo de artigo científico para revisão PRISMA
AU  - Sobrenome, Nome
PY  - 2026
JO  - Revista Científica
DO  - 10.0000/exemplo
ER  -
"""

    caminho = "outputs/references/referencias_exemplo.ris"

    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(conteudo)

    print(f"Arquivo RIS para Zotero gerado em: {caminho}")


def main():

    criar_pastas()

    parametros = coletar_parametros()

    gerar_tabela_inicial(parametros)

    gerar_descricao_figura_prisma(parametros)

    gerar_referencia_zotero_exemplo()

    print("\nRobô executado com sucesso!")
    print("Verifique a pasta outputs.")


if __name__ == "__main__":
    main()