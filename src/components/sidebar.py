from src.utils.nomes_arquivos import limpar_nome_arquivo, caminho_saida_seguro
import os
import glob
import shutil
import streamlit as st


def render_sidebar_manutencao():
    with st.sidebar.expander("⚙️ Manutenção", expanded=False):

        st.caption("Use estas opções para limpar arquivos gerados sem alterar o banco de dados da revisão.")

        if st.button("🗑 Limpar arquivos da última revisão"):
            removidos = 0

            pastas = ["outputs", "exports"]
            padroes = [
                "ATHENA_PRISMA_*",
                "Fluxograma_PRISMA*",
                "fluxograma_prisma*",
                "*.ris",
                "*.bib",
                "referencias_*",
            ]

            for pasta in pastas:
                if os.path.isdir(pasta):
                    for padrao in padroes:
                        for arq in glob.glob(os.path.join(pasta, padrao)):
                            if os.path.isfile(arq):
                                os.remove(arq)
                                removidos += 1

            st.success(f"Arquivos removidos: {removidos}")
            st.rerun()

        if st.button("🧹 Limpar backups"):
            removidos = 0

            pastas = ["src", "src/outputs"]
            for pasta in pastas:
                if os.path.isdir(pasta):
                    for arq in glob.glob(os.path.join(pasta, "*.bak_*")):
                        if os.path.isfile(arq):
                            os.remove(arq)
                            removidos += 1

            st.success(f"Backups removidos: {removidos}")
            st.rerun()

        if st.button("♻️ Limpar cache temporário"):
            removidos = 0

            pastas_cache = [
                "src/__pycache__",
                "src/outputs/__pycache__",
                "src/buscadores/__pycache__",
                "src/prisma/__pycache__",
                "src/ia/__pycache__",
                "src/apis/__pycache__",
            ]

            for pasta in pastas_cache:
                if os.path.isdir(pasta):
                    shutil.rmtree(pasta)
                    removidos += 1

            st.success(f"Pastas de cache removidas: {removidos}")
            st.rerun()
