from src.utils.nomes_arquivos import limpar_nome_arquivo, caminho_saida_seguro
from pathlib import Path


def gerar_referencias_abnt(artigos, caminho="outputs/references/referencias_abnt.txt"):
    Path(caminho).parent.mkdir(parents=True, exist_ok=True)

    linhas = []

    for art in artigos:
        autores = art.get("autores", "").upper()
        titulo = art.get("titulo", "")
        ano = art.get("ano", "")
        doi = art.get("doi", "")
        url = art.get("url", "")

        ref = f"{autores}. {titulo}. {ano}."
        if doi:
            ref += f" DOI: {doi}."
        elif url:
            ref += f" Disponível em: {url}."

        linhas.append(ref)

    Path(caminho).write_text("\n\n".join(linhas), encoding="utf-8")

    return caminho
