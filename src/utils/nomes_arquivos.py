from pathlib import Path
from datetime import datetime
import re
import unicodedata
import hashlib

def limpar_nome_arquivo(texto, max_len=60):
    texto = str(texto or "busca")
    texto_original = texto

    texto = unicodedata.normalize("NFKD", texto)
    texto = texto.encode("ascii", "ignore").decode("ascii")
    texto = texto.lower()
    texto = re.sub(r"[^a-z0-9]+", "_", texto)
    texto = texto.strip("_")

    if not texto:
        texto = "busca"

    if len(texto) > max_len:
        hash_curto = hashlib.md5(texto_original.encode("utf-8")).hexdigest()[:8]
        texto = texto[:max_len].rstrip("_") + "_" + hash_curto

    return texto

def caminho_saida_seguro(pasta, prefixo, tema=None, extensao="xlsx", max_len=60):
    Path(pasta).mkdir(parents=True, exist_ok=True)
    nome_limpo = limpar_nome_arquivo(tema or prefixo, max_len=max_len)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extensao = extensao.lstrip(".")
    return Path(pasta) / f"{prefixo}_{nome_limpo}_{timestamp}.{extensao}"
