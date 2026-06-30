import re
import unicodedata


STOPWORDS = {
    "a", "o", "as", "os", "um", "uma", "uns", "umas",
    "de", "do", "da", "dos", "das",
    "em", "no", "na", "nos", "nas",
    "e", "ou", "para", "por", "com", "sem", "sobre", "entre",
    "uso", "utilizacao", "utilização", "avaliacao", "avaliação",
    "analise", "análise", "estudo", "efeito", "impacto",
    "publico", "público", "populacao", "população"
}


SINONIMOS = {
    "dermocosmetico": [
        "dermocosmetic*", "cosmeceutical*", "cosmetic*",
        "skin care", "skin care product*", "topical cosmetic*",
        "emollient*", "moisturizer*", "moisturiser*", "barrier cream*"
    ],
    "dermocosmeticos": [
        "dermocosmetic*", "cosmeceutical*", "cosmetic*",
        "skin care", "skin care product*", "topical cosmetic*",
        "emollient*", "moisturizer*", "moisturiser*", "barrier cream*"
    ],
    "pediatrico": [
        "child*", "children", "pediatric*", "paediatric*",
        "infant*", "newborn*", "neonate*", "adolescent*", "teen*", "youth"
    ],
    "pediatria": [
        "child*", "children", "pediatric*", "paediatric*",
        "infant*", "newborn*", "neonate*", "adolescent*", "teen*", "youth"
    ],
    "crianca": [
        "child*", "children", "pediatric*", "paediatric*",
        "infant*", "newborn*", "neonate*", "adolescent*"
    ],
    "criancas": [
        "child*", "children", "pediatric*", "paediatric*",
        "infant*", "newborn*", "neonate*", "adolescent*"
    ],
    "dermatite": [
        "dermatitis", "atopic dermatitis", "eczema", "atopic eczema"
    ],
    "acne": [
        "acne", "acne vulgaris", "comedone*", "inflammatory acne"
    ],
    "covid": [
        "COVID-19", "SARS-CoV-2", "coronavirus disease 2019", "coronavirus"
    ],
    "diabetes": [
        "diabetes mellitus", "diabetes", "type 1 diabetes", "type 2 diabetes", "T1DM", "T2DM"
    ],
    "hipertensao": [
        "hypertension", "high blood pressure", "hypertensive disease"
    ],
    "microbiota": [
        "microbiota", "gut microbiota", "intestinal microbiota", "gut flora", "microbiome"
    ],
    "ansiedade": [
        "anxiety", "anxiety disorder", "psychological stress"
    ],
    "depressao": [
        "depression", "depressive symptoms", "major depression"
    ],
    "takotsubo": [
        "Takotsubo cardiomyopathy", "Takotsubo syndrome",
        "stress cardiomyopathy", "stress-induced cardiomyopathy",
        "broken heart syndrome", "apical ballooning syndrome"
    ],
    "brasil": [
        "Brazil", "Brasil", "Brazilian"
    ],
}


MESH = {
    "dermocosmetico": ["Cosmetics", "Skin Care"],
    "dermocosmeticos": ["Cosmetics", "Skin Care"],
    "pediatrico": ["Child", "Infant", "Adolescent", "Pediatrics"],
    "pediatria": ["Child", "Infant", "Adolescent", "Pediatrics"],
    "crianca": ["Child", "Infant", "Adolescent"],
    "criancas": ["Child", "Infant", "Adolescent"],
    "dermatite": ["Dermatitis, Atopic", "Eczema"],
    "acne": ["Acne Vulgaris"],
    "covid": ["COVID-19", "SARS-CoV-2"],
    "diabetes": ["Diabetes Mellitus"],
    "hipertensao": ["Hypertension"],
    "microbiota": ["Gastrointestinal Microbiome", "Microbiota"],
    "ansiedade": ["Anxiety"],
    "depressao": ["Depression"],
}


EXPRESSOES_COMPOSTAS = {
    "dermatite atopica": {
        "sinonimos": ["atopic dermatitis", "atopic eczema", "eczema"],
        "mesh": ["Dermatitis, Atopic"]
    },
    "publico pediatrico": {
        "sinonimos": ["child*", "children", "pediatric*", "paediatric*", "infant*", "adolescent*"],
        "mesh": ["Child", "Infant", "Adolescent", "Pediatrics"]
    },
    "saude mental": {
        "sinonimos": ["mental health", "psychological health", "emotional health"],
        "mesh": ["Mental Health"]
    },
    "estudantes de medicina": {
        "sinonimos": ["medical students", "medicine students", "undergraduate medical students"],
        "mesh": ["Students, Medical", "Education, Medical"]
    },
}


def remover_acentos(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in texto if not unicodedata.combining(c))


def limpar_texto(texto: str) -> str:
    texto = texto.lower().strip()
    texto = remover_acentos(texto)
    texto = texto.replace(",", " ")
    texto = re.sub(r"[^a-zA-Z0-9\s\-]", " ", texto)
    texto = re.sub(r"\s+", " ", texto)
    return texto.strip()


def formatar_tiab(termo: str) -> str:
    if "*" in termo:
        return f'{termo}[Title/Abstract]'
    return f'"{termo}"[Title/Abstract]'


def formatar_mesh(termo: str) -> str:
    return f'"{termo}"[Mesh]'


def bloco_booleano(termos, mesh=None):
    termos = list(dict.fromkeys([t for t in termos if t]))
    mesh = list(dict.fromkeys(mesh or []))

    partes = [formatar_tiab(t) for t in termos]
    partes += [formatar_mesh(m) for m in mesh]

    if not partes:
        return ""

    return "(" + " OR ".join(partes) + ")"


def detectar_conceitos(entrada_usuario: str):
    texto = limpar_texto(entrada_usuario)
    conceitos = []

    for expressao, dados in EXPRESSOES_COMPOSTAS.items():
        if expressao in texto:
            conceitos.append({
                "termo": expressao,
                "sinonimos": dados["sinonimos"],
                "mesh": dados["mesh"]
            })
            texto = texto.replace(expressao, " ")

    palavras = [
        p for p in texto.split()
        if p and p not in STOPWORDS and len(p) > 2
    ]

    for palavra in palavras:
        conceitos.append({
            "termo": palavra,
            "sinonimos": SINONIMOS.get(palavra, [palavra]),
            "mesh": MESH.get(palavra, [])
        })

    # deduplicação por termo
    vistos = set()
    unicos = []
    for c in conceitos:
        if c["termo"] not in vistos:
            unicos.append(c)
            vistos.add(c["termo"])

    return unicos


def termos_revisao(tipo_revisao: str = ""):
    tipo = limpar_texto(tipo_revisao or "")

    if "escopo" in tipo or "scoping" in tipo:
        return [
            '"scoping review"[Title/Abstract]',
            '"mapping review"[Title/Abstract]',
            '"evidence map"[Title/Abstract]'
        ]

    if "integrativa" in tipo or "integrative" in tipo:
        return [
            '"integrative review"[Title/Abstract]',
            '"literature review"[Title/Abstract]',
            '"review"[Publication Type]'
        ]

    if "narrativa" in tipo or "narrative" in tipo:
        return [
            '"narrative review"[Title/Abstract]',
            '"literature review"[Title/Abstract]',
            '"review"[Publication Type]'
        ]

    return [
        '"systematic review"[Publication Type]',
        '"meta-analysis"[Publication Type]',
        '"systematic review"[Title/Abstract]',
        '"meta-analysis"[Title/Abstract]',
        '"evidence synthesis"[Title/Abstract]'
    ]


def gerar_booleano(entrada_usuario, tipo_revisao="Revisão sistemática"):
    conceitos = detectar_conceitos(entrada_usuario)

    blocos = []
    for conceito in conceitos:
        bloco = bloco_booleano(
            conceito["sinonimos"],
            conceito.get("mesh", [])
        )
        if bloco:
            blocos.append(bloco)

    bloco_revisao = "(" + " OR ".join(termos_revisao(tipo_revisao)) + ")"
    blocos.append(bloco_revisao)

    if not blocos:
        return ""

    return "\nAND\n".join(blocos)


def gerar_estrategias_multibase(entrada_usuario, tipo_revisao="Revisão sistemática"):
    pubmed = gerar_booleano(entrada_usuario, tipo_revisao)

    conceitos = detectar_conceitos(entrada_usuario)
    blocos_simples = []
    for c in conceitos:
        termos = []
        for t in c["sinonimos"]:
            if "*" in t:
                termos.append(t)
            else:
                termos.append(f'"{t}"')
        blocos_simples.append("(" + " OR ".join(termos) + ")")

    review = '("systematic review" OR "meta-analysis" OR "scoping review" OR "integrative review" OR "narrative review" OR "evidence synthesis")'
    corpo = " AND ".join(blocos_simples + [review])

    return {
        "PubMed": pubmed,
        "Scopus": f"TITLE-ABS-KEY({corpo})",
        "Web of Science": f"TS=({corpo})",
        "SciELO": corpo,
        "LILACS": corpo,
        "Google Scholar": corpo,
    }
