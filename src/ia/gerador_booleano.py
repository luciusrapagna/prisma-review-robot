import re


SINONIMOS = {

    "takotsubo": [
        "Takotsubo cardiomyopathy",
        "Takotsubo syndrome",
        "stress cardiomyopathy",
        "stress-induced cardiomyopathy",
        "broken heart syndrome",
        "apical ballooning syndrome"
    ],

    "microbiota": [
        "microbiota",
        "gut microbiota",
        "intestinal microbiota",
        "gut flora"
    ],

    "depressao": [
        "depression",
        "depressive symptoms",
        "major depression"
    ],

    "ansiedade": [
        "anxiety",
        "anxiety disorder",
        "stress"
    ],

    "medicina": [
        "medical students",
        "medicine students",
        "medical education"
    ],

    "brasil": [
        "Brazil",
        "Brasil",
        "Brazilian"
    ],

    "covid": [
        "COVID-19",
        "SARS-CoV-2",
        "coronavirus"
    ],

    "mortalidade": [
        "mortality",
        "death",
        "survival",
        "outcomes"
    ],

    "diagnostico": [
        "diagnosis",
        "diagnostic",
        "screening"
    ],

    "tratamento": [
        "treatment",
        "therapy",
        "management"
    ]
}


def limpar_texto(texto):

    texto = texto.lower()

    texto = texto.replace(",", " ")

    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


def gerar_booleano(entrada_usuario):

    entrada_usuario = limpar_texto(entrada_usuario)

    palavras = entrada_usuario.split()

    grupos_booleanos = []

    for palavra in palavras:

        palavra = palavra.strip()

        if not palavra:
            continue

        sinonimos = SINONIMOS.get(
            palavra,
            [palavra]
        )

        bloco = " OR ".join(
            [f'"{s}"[Title/Abstract]' for s in sinonimos]
        )

        bloco = f"({bloco})"

        grupos_booleanos.append(bloco)

    booleano_final = "\nAND\n".join(grupos_booleanos)

    return booleano_final