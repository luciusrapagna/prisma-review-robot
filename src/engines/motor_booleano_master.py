"""
ATHENA PRISMA — Motor Booleano Master

Motor único para geração de estratégias bibliográficas multibase.

Responsabilidades:
- identificar conceitos científicos;
- expandir conceitos com termos livres e vocabulário controlado;
- combinar sinônimos com OR;
- combinar conceitos com AND;
- gerar estratégias compatíveis com PubMed, SciELO, LILACS
  e buscadores acadêmicos gerais.

Este módulo substitui os antigos:
- ia/gerador_booleano.py
- engines/motor_busca_multilingue.py
"""

from __future__ import annotations

import re
import unicodedata
from typing import Dict, Iterable, List


STOPWORDS = {
    "a", "ao", "aos", "as", "com", "como", "da", "das", "de", "do",
    "dos", "e", "em", "entre", "na", "nas", "no", "nos", "o", "os",
    "ou", "para", "por", "que", "se", "sobre", "um", "uma", "uso",
    "efeito", "efeitos", "publico", "público",
}


CONCEITOS: Dict[str, Dict[str, List[str]]] = {
    "dermocosmeticos": {
        "gatilhos": [
            "dermocosmetico",
            "dermocosmeticos",
            "dermocosmético",
            "dermocosméticos",
            "cosmetico",
            "cosmeticos",
            "cosmético",
            "cosméticos",
            "skincare",
            "skin care",
        ],
        "pubmed": [
            '"Cosmetics"[MeSH Terms]',
            'cosmetic*[Title/Abstract]',
            'dermocosmetic*[Title/Abstract]',
            '"skin care"[Title/Abstract]',
            'skincare[Title/Abstract]',
            '"personal care product*"[Title/Abstract]',
            '"topical cosmetic*"[Title/Abstract]',
        ],
        "latam": [
            'dermocosmético*',
            'dermocosmetico*',
            'cosmético*',
            'cosmetico*',
            '"cuidados com a pele"',
            '"cuidado de la piel"',
            '"produto de cuidado pessoal"',
            '"producto de cuidado personal"',
            '"skin care"',
            'skincare',
        ],
        "geral": [
            'dermocosmetic*',
            'cosmetic*',
            '"skin care"',
            'skincare',
            '"personal care product*"',
            '"topical cosmetic*"',
            'dermocosmético*',
            'cosmético*',
        ],
    },

    "pediatria": {
        "gatilhos": [
            "pediatrico",
            "pediatrica",
            "pediatricos",
            "pediatricas",
            "pediátrico",
            "pediátrica",
            "pediátricos",
            "pediátricas",
            "pediatric",
            "paediatric",
            "crianca",
            "criancas",
            "criança",
            "crianças",
            "infantil",
            "infancia",
            "infância",
            "adolescente",
            "adolescentes",
            "bebê",
            "bebe",
            "infant",
            "child",
            "children",
        ],
        "pubmed": [
            '"Child"[MeSH Terms]',
            '"Infant"[MeSH Terms]',
            '"Adolescent"[MeSH Terms]',
            'child*[Title/Abstract]',
            'pediatric*[Title/Abstract]',
            'paediatric*[Title/Abstract]',
            'infant*[Title/Abstract]',
            'adolescen*[Title/Abstract]',
            'newborn*[Title/Abstract]',
        ],
        "latam": [
            'criança*',
            'crianca*',
            'infância',
            'infancia',
            'pediátric*',
            'pediatric*',
            'infantil',
            'adolescente*',
            'niño*',
            'niña*',
            'infancia',
        ],
        "geral": [
            'child*',
            'children',
            'pediatric*',
            'paediatric*',
            'infant*',
            'adolescen*',
            'newborn*',
            'criança*',
            'pediátric*',
        ],
    },

    "eventos_adversos": {
        "gatilhos": [
            "efeito nocivo",
            "efeitos nocivos",
            "evento adverso",
            "eventos adversos",
            "reacao adversa",
            "reacoes adversas",
            "reação adversa",
            "reações adversas",
            "toxicidade",
            "toxico",
            "tóxico",
            "seguranca",
            "segurança",
            "dano",
            "danos",
            "irritacao",
            "irritação",
            "adverse effect",
            "adverse effects",
            "adverse event",
            "adverse events",
            "toxicity",
            "safety",
            "harm",
        ],
        "pubmed": [
            '"Drug-Related Side Effects and Adverse Reactions"[MeSH Terms]',
            '"adverse effect*"[Title/Abstract]',
            '"adverse event*"[Title/Abstract]',
            '"adverse reaction*"[Title/Abstract]',
            'toxic*[Title/Abstract]',
            'safety[Title/Abstract]',
            'harm*[Title/Abstract]',
            'irritation[Title/Abstract]',
            'dermatitis[Title/Abstract]',
            'sensitization[Title/Abstract]',
        ],
        "latam": [
            '"efeito adverso"',
            '"efeitos adversos"',
            '"evento adverso"',
            '"eventos adversos"',
            '"reação adversa"',
            '"reacciones adversas"',
            'toxicidade',
            'toxicidad',
            'segurança',
            'seguridad',
            'dano*',
            'irritação',
            'irritación',
        ],
        "geral": [
            '"adverse effect*"',
            '"adverse event*"',
            '"adverse reaction*"',
            'toxic*',
            'safety',
            'harm*',
            'irritation',
            'dermatitis',
            'sensitization',
        ],
    },

    "imagem": {
        "gatilhos": [
            "imagem",
            "exames de imagem",
            "diagnostico por imagem",
            "diagnóstico por imagem",
            "radiografia",
            "raio x",
            "ultrassom",
            "ultrassonografia",
            "tomografia",
            "imaging",
        ],
        "pubmed": [
            '"Diagnostic Imaging"[MeSH Terms]',
            '"diagnostic imaging"[Title/Abstract]',
            '"medical imaging"[Title/Abstract]',
            'radiograph*[Title/Abstract]',
            'ultrasound[Title/Abstract]',
            'ultrasonograph*[Title/Abstract]',
            '"computed tomography"[Title/Abstract]',
        ],
        "latam": [
            '"diagnóstico por imagem"',
            '"diagnostico por imagem"',
            '"exames de imagem"',
            'radiografia',
            '"raio x"',
            'ultrassom',
            'ultrassonografia',
            'tomografia',
            '"diagnóstico por imagen"',
            'radiografía',
            'ultrasonografía',
            'tomografía',
        ],
        "geral": [
            '"diagnostic imaging"',
            '"medical imaging"',
            'radiograph*',
            'ultrasound',
            'ultrasonograph*',
            '"computed tomography"',
        ],
    },

    "pneumotorax": {
        "gatilhos": [
            "pneumotorax",
            "pneumotórax",
            "pneumothorax",
            "neumotorax",
            "neumotórax",
            "peneumotorax",
        ],
        "pubmed": [
            '"Pneumothorax"[MeSH Terms]',
            'pneumothorax[Title/Abstract]',
            'pneumothoraces[Title/Abstract]',
        ],
        "latam": [
            'pneumotórax',
            'pneumotorax',
            'pneumothorax',
            'neumotórax',
            'neumotorax',
        ],
        "geral": [
            'pneumothorax',
            'pneumothoraces',
            'pneumotórax',
            'neumotórax',
        ],
    },

    "diagnostico": {
        "gatilhos": [
            "diagnostico",
            "diagnóstico",
            "diagnosis",
            "diagnostic",
            "deteccao",
            "detecção",
        ],
        "pubmed": [
            '"Diagnosis"[MeSH Terms]',
            'diagnos*[Title/Abstract]',
            '"diagnostic accuracy"[Title/Abstract]',
            'detection[Title/Abstract]',
            'sensitivity[Title/Abstract]',
            'specificity[Title/Abstract]',
        ],
        "latam": [
            'diagnóstico',
            'diagnostico',
            'diagnosis',
            'diagnostic',
            'detecção',
            'detección',
            'sensibilidade',
            'especificidade',
            'sensibilidad',
            'especificidad',
        ],
        "geral": [
            'diagnos*',
            '"diagnostic accuracy"',
            'detection',
            'sensitivity',
            'specificity',
        ],
    },

    "tratamento": {
        "gatilhos": [
            "tratamento",
            "terapia",
            "therapy",
            "treatment",
            "management",
        ],
        "pubmed": [
            '"Therapeutics"[MeSH Terms]',
            'treatment*[Title/Abstract]',
            'therap*[Title/Abstract]',
            'management[Title/Abstract]',
        ],
        "latam": [
            'tratamento*',
            'terapia*',
            'manejo',
            'tratamiento*',
        ],
        "geral": [
            'treatment*',
            'therap*',
            'management',
        ],
    },

    "mortalidade": {
        "gatilhos": [
            "mortalidade",
            "morte",
            "sobrevida",
            "mortality",
            "death",
            "survival",
        ],
        "pubmed": [
            '"Mortality"[MeSH Terms]',
            'mortality[Title/Abstract]',
            'death*[Title/Abstract]',
            'survival[Title/Abstract]',
        ],
        "latam": [
            'mortalidade',
            'morte*',
            'sobrevida',
            'mortalidad',
            'muerte*',
            'supervivencia',
        ],
        "geral": [
            'mortality',
            'death*',
            'survival',
        ],
    },

    "covid": {
        "gatilhos": [
            "covid",
            "covid-19",
            "sars-cov-2",
            "sars cov 2",
            "coronavirus",
        ],
        "pubmed": [
            '"COVID-19"[MeSH Terms]',
            '"SARS-CoV-2"[MeSH Terms]',
            'COVID-19[Title/Abstract]',
            'SARS-CoV-2[Title/Abstract]',
            'coronavirus[Title/Abstract]',
        ],
        "latam": [
            'COVID-19',
            'SARS-CoV-2',
            'coronavírus',
            'coronavirus',
        ],
        "geral": [
            'COVID-19',
            'SARS-CoV-2',
            'coronavirus',
        ],
    },

    "brasil": {
        "gatilhos": [
            "brasil",
            "brazil",
            "brazilian",
        ],
        "pubmed": [
            '"Brazil"[MeSH Terms]',
            'Brazil[Title/Abstract]',
            'Brazilian[Title/Abstract]',
        ],
        "latam": [
            'Brasil',
            'Brazil',
            'brasileir*',
            'brasileñ*',
        ],
        "geral": [
            'Brazil',
            'Brazilian',
            'Brasil',
        ],
    },

    "educacao_medica": {
        "gatilhos": [
            "educacao medica",
            "educação médica",
            "estudante de medicina",
            "estudantes de medicina",
            "medical education",
            "medical student",
            "medical students",
        ],
        "pubmed": [
            '"Education, Medical"[MeSH Terms]',
            '"Students, Medical"[MeSH Terms]',
            '"medical education"[Title/Abstract]',
            '"medical student*"[Title/Abstract]',
        ],
        "latam": [
            '"educação médica"',
            '"educacao medica"',
            '"estudante de medicina"',
            '"estudiantes de medicina"',
            '"educación médica"',
        ],
        "geral": [
            '"medical education"',
            '"medical student*"',
            '"educação médica"',
        ],
    },
}


def normalizar(texto: str) -> str:
    texto = str(texto or "").lower().strip()
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caractere
        for caractere in texto
        if not unicodedata.combining(caractere)
    )
    texto = re.sub(r"[^a-z0-9\s;,\-]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def remover_duplicatas(termos: Iterable[str]) -> List[str]:
    resultado: List[str] = []
    vistos = set()

    for termo in termos:
        termo = str(termo).strip()

        if not termo:
            continue

        chave = termo.casefold()

        if chave in vistos:
            continue

        vistos.add(chave)
        resultado.append(termo)

    return resultado


def detectar_conceitos(tema: str) -> List[str]:
    tema_normalizado = normalizar(tema)
    detectados: List[str] = []

    for conceito, dados in CONCEITOS.items():
        for gatilho in dados["gatilhos"]:
            gatilho_normalizado = normalizar(gatilho)

            if gatilho_normalizado and gatilho_normalizado in tema_normalizado:
                detectados.append(conceito)
                break

    return remover_duplicatas(detectados)


def extrair_blocos_explicitos(tema: str) -> List[str]:
    partes = [
        parte.strip()
        for parte in re.split(r"[;|]", str(tema or ""))
        if parte.strip()
    ]

    if len(partes) <= 1:
        return []

    return remover_duplicatas(partes)


def criar_fallback(tema: str, base: str) -> str:
    palavras = [
        palavra
        for palavra in normalizar(tema).split()
        if palavra not in STOPWORDS and len(palavra) > 2
    ]

    palavras = remover_duplicatas(palavras)

    if not palavras:
        return ""

    expressao = " ".join(palavras)

    if base == "pubmed":
        return f'("{expressao}"[Title/Abstract])'

    return f'("{expressao}")'


def formatar_bloco(termos: Iterable[str]) -> str:
    termos_limpos = remover_duplicatas(termos)

    if not termos_limpos:
        return ""

    return "(\n  " + "\n  OR ".join(termos_limpos) + "\n)"


def converter_bloco_explicito(bloco: str, base: str) -> str:
    bloco = bloco.strip()

    if not bloco:
        return ""

    if base == "pubmed":
        return formatar_bloco([
            f'"{bloco}"[Title/Abstract]',
        ])

    return formatar_bloco([
        f'"{bloco}"',
    ])


def gerar_query_por_base(tema: str, base: str) -> str:
    if not tema or not str(tema).strip():
        return ""

    conceitos = detectar_conceitos(tema)
    blocos: List[str] = []

    for conceito in conceitos:
        dados = CONCEITOS[conceito]
        termos = dados.get(base) or dados["geral"]
        bloco = formatar_bloco(termos)

        if bloco:
            blocos.append(bloco)

    blocos_explicitos = extrair_blocos_explicitos(tema)

    if blocos_explicitos and not conceitos:
        for item in blocos_explicitos:
            bloco = converter_bloco_explicito(item, base)

            if bloco:
                blocos.append(bloco)

    if not blocos:
        return criar_fallback(tema, base)

    return "\nAND\n".join(remover_duplicatas(blocos))


def gerar_relatorio(
    tema: str,
    tipo_revisao: str,
    conceitos: List[str],
) -> Dict[str, object]:
    return {
        "tema": tema,
        "tipo_revisao": tipo_revisao,
        "conceitos_identificados": conceitos,
        "numero_conceitos": len(conceitos),
        "estrutura": "OR dentro dos blocos; AND entre os blocos",
        "observacao": (
            "Estratégia automatizada. Recomenda-se validação final por "
            "pesquisador ou bibliotecário especialista."
        ),
    }


def gerar_estrategias(
    tema: str,
    tipo_revisao: str = "Revisão sistemática",
) -> Dict[str, object]:
    conceitos = detectar_conceitos(tema)

    query_pubmed = gerar_query_por_base(tema, "pubmed")
    query_latam = gerar_query_por_base(tema, "latam")
    query_geral = gerar_query_por_base(tema, "geral")

    return {
        "query_pubmed": query_pubmed,
        "query_scielo": query_latam,
        "query_lilacs": query_latam,
        "query_bvs": query_latam,
        "query_geral": query_geral,
        "query_google_scholar": query_geral,
        "query_busca_ampliada": query_geral,
        "relatorio": gerar_relatorio(
            tema=tema,
            tipo_revisao=tipo_revisao,
            conceitos=conceitos,
        ),
    }


def gerar_booleano(
    tema: str,
    tipo_revisao: str = "Revisão sistemática",
) -> str:
    """
    Função de compatibilidade.

    Retorna a estratégia PubMed produzida pelo motor master.
    """
    return str(
        gerar_estrategias(
            tema=tema,
            tipo_revisao=tipo_revisao,
        )["query_pubmed"]
    )


__all__ = [
    "CONCEITOS",
    "detectar_conceitos",
    "gerar_booleano",
    "gerar_estrategias",
    "gerar_query_por_base",
]
