import re
import unicodedata


def normalizar_texto(texto):
    texto = str(texto or "")
    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = texto.lower().strip()
    texto = re.sub(r"\s+", " ", texto)
    texto = re.sub(r"[^a-z0-9 ]", "", texto)
    return texto


def remover_duplicatas(artigos):
    """Remove duplicatas de uma lista de artigos.

    A funcao usa DOI preferencialmente. Se DOI estiver ausente,
    usa titulo normalizado, PMID ou link como chave de deteccao.
    """
    chaves_vistas = set()
    artigos_unicos = []

    for artigo in artigos:
        doi = normalizar_texto(artigo.get("DOI", ""))
        if doi:
            chave = f"doi:{doi}"
        else:
            titulo = normalizar_texto(artigo.get("Titulo", "") or artigo.get("title", ""))
            if titulo:
                chave = f"title:{titulo}"
            else:
                pmid = str(artigo.get("PMID", "") or "").strip()
                if pmid:
                    chave = f"pmid:{pmid}"
                else:
                    link = normalizar_texto(artigo.get("Link", ""))
                    chave = f"link:{link}"

        if chave and chave not in chaves_vistas:
            chaves_vistas.add(chave)
            artigos_unicos.append(artigo)

    return artigos_unicos
