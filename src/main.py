
from database.historico import (
    salvar_revisao,
    listar_revisoes
)

from exports.abnt import gerar_referencias_abnt

from prisma_flow.fluxograma import gerar_fluxograma_prisma


import streamlit as st

st.set_page_config(
    page_title="PRISMA Review Robot",
    page_icon="📚",
    layout="wide"
)

st.title("📚 PRISMA Review Robot")
st.subheader("ATHENA Scientific — Revisões Sistemáticas Inteligentes")

st.markdown("""
Sistema automatizado para:
- busca bibliográfica multibase
- remoção de duplicatas
- ranking semântico por IA
- geração automática de relatórios PRISMA
- exportação Word, tabelas e RIS Zotero
""")


historico = listar_revisoes()

with st.sidebar:
    st.header("📚 Histórico ATHENA")

    if historico:
        for item in historico[:10]:
            st.caption(
                f"{item[1]} | {item[8]}"
            )
    else:
        st.info("Nenhuma revisão registrada.")

st.divider()


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

from ia.gerador_booleano import gerar_booleano

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
    import streamlit as st
    from datetime import date

    tema = st.text_input("Digite o tema da revisão", value="dengue")

    tipo_revisao = st.selectbox(
        "Tipo de revisão",
        ["Revisão sistemática", "Revisão de escopo", "Revisão integrativa", "Revisão narrativa"],
        index=1
    )

    query_geral = st.text_area(
        "Estratégia de busca / query geral",
        value=f'("{tema}") AND ("review" OR "systematic review" OR "scoping review")'
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        ano_inicial = st.number_input("Ano inicial", min_value=1900, max_value=2100, value=2014, step=1)
    with col2:
        ano_final = st.number_input("Ano final", min_value=1900, max_value=2100, value=2026, step=1)
    with col3:
        max_artigos = st.number_input("Número máximo de artigos", min_value=1, max_value=1000, value=30, step=1)

    data_execucao = st.date_input("Data de execução", value=date.today())

    bases = st.multiselect(
        "Bases de dados",
        ["PubMed", "Scopus", "Web of Science", "SciELO", "LILACS", "BVS", "Google Scholar"],
        default=["PubMed", "SciELO", "LILACS"]
    )

    idioma = st.multiselect(
        "Idiomas",
        ["Português", "Inglês", "Espanhol"],
        default=["Português", "Inglês", "Espanhol"]
    )

    tipo_estudo = st.text_input("Tipo de estudo", value=tipo_revisao)

    if not tema:
        st.warning("Informe o tema da revisão para continuar.")
        st.stop()

    return {
        "tema": tema,
        "tipo_revisao": tipo_revisao,
        "query_geral": query_geral,
        "query_pubmed": query_geral,
        "query_scielo": query_geral,
        "query_lilacs": query_geral,
        "ano_inicial": int(ano_inicial),
        "ano_final": int(ano_final),
        "max_artigos": int(max_artigos),
        "bases": ", ".join(bases),
        "idioma": ", ".join(idioma),
        "tipo_estudo": tipo_estudo,
        "data_execucao": data_execucao.strftime("%d/%m/%Y")
    }


def perguntar_similaridade():
    import streamlit as st

    valor = st.number_input(
        "Digite a similaridade mínima desejada",
        min_value=0.0,
        max_value=1.0,
        value=0.35,
        step=0.05
    )

    return float(valor)


def gerar_tabela_parametros(parametros, similaridade_minima):
    dados = {
        "Campo": [
            "Tema",
            "Ano inicial",
            "Ano final",
            "EstratAgia de busca",
            "MAximo de artigos por base",
            "Tipo de revisAo",
            "Similaridade mAnima",
            "Data de execuAAo"
        ],
        "InformaAAo": [
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

    print(f"\nTabela de parAmetros gerada em: {caminho}")


def salvar_tabela_consolidada(artigos):
    caminho = "outputs/tables/tabela_consolidada_multibase.xlsx"

    if not artigos:
        df = pd.DataFrame(columns=[
            "Base",
            "PMID",
            "TAtulo",
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

    caminho = "outputs/figures/descricao_figura_prisma.txt"

    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto)

    print(f"\nDescriAAo da figura PRISMA gerada em: {caminho}")


def gerar_ris_zotero(artigos):
    caminho = "outputs/references/referencias_multibase.ris"

    with open(caminho, "w", encoding="utf-8") as arquivo:
        for artigo in artigos:
            arquivo.write("TY  - JOUR\n")
            arquivo.write(f"TI  - {artigo.get('TAtulo', '')}\n")
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

    import streamlit as st

    executar = st.button("🚀 Executar revisão")

    if not executar:
        st.stop()

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

    gerar_referencias_abnt(artigos_rankeados)

    svg_fluxo, pdf_fluxo = gerar_fluxograma_prisma(
        total_identificados=total_identificados,
        total_sem_duplicatas=total_sem_duplicatas,
        total_apos_similaridade=total_apos_similaridade
    )

    salvar_revisao(
        parametros=parametros,
        total_identificados=total_identificados,
        total_pos_duplicatas=total_sem_duplicatas,
        total_pos_similaridade=total_apos_similaridade
    )


    import streamlit as st
    from pathlib import Path
    import zipfile
    from io import BytesIO

    st.success("✅ Robô PRISMA executado com sucesso!")

    st.write(f"**PubMed:** {total_pubmed} registros")
    st.write(f"**Crossref:** {total_crossref} registros")
    st.write(f"**SciELO:** {total_scielo} registros")
    st.write(f"**LILACS/BVS:** {total_lilacs} registros")
    st.write(f"**Total identificado:** {total_identificados} registros")
    st.write(f"**Total após duplicatas:** {total_sem_duplicatas} registros")
    st.write(f"**Total após similaridade:** {total_apos_similaridade} registros")
    st.write(f"**Similaridade mínima usada:** {similaridade_minima}")

    st.subheader("📊 Fluxograma PRISMA")

    st.image(svg_fluxo)

    with open(svg_fluxo, "rb") as f:
        st.download_button(
            "🖼️ Baixar fluxograma SVG",
            f,
            file_name="fluxograma_prisma.svg",
            mime="image/svg+xml"
        )

    with open(pdf_fluxo, "rb") as f:
        st.download_button(
            "📄 Baixar fluxograma PDF",
            f,
            file_name="fluxograma_prisma.pdf",
            mime="application/pdf"
        )

    st.subheader("📁 Arquivos gerados")

    caminho_relatorio = Path(caminho_relatorio)

    if caminho_relatorio.exists():
        with open(caminho_relatorio, "rb") as f:
            st.download_button(
                "📄 Baixar relatório Word",
                f,
                file_name=caminho_relatorio.name,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

    memoria_zip = BytesIO()

    with zipfile.ZipFile(memoria_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for pasta in ["outputs/tables", "outputs/figures", "outputs/references"]:
            p = Path(pasta)
            if p.exists():
                for arquivo_saida in p.rglob("*"):
                    if arquivo_saida.is_file():
                        zipf.write(arquivo_saida, arquivo_saida.as_posix())

    memoria_zip.seek(0)

    st.download_button(
        "📦 Baixar todos os arquivos gerados",
        memoria_zip,
        file_name="prisma_outputs.zip",
        mime="application/zip"
    )



if __name__ == "__main__":
    main()
