def gerar_booleano(tema: str, tipo_revisao: str = "Revisão Sistemática") -> str:
    tema_lower = tema.lower()

    # Tema: dermocosméticos em público pediátrico
    if "dermocosm" in tema_lower or "cosmético" in tema_lower or "cosmetico" in tema_lower:
        populacao = """(
child*[Title/Abstract] OR children[Title/Abstract] OR pediatric*[Title/Abstract] OR paediatric*[Title/Abstract]
OR infant*[Title/Abstract] OR newborn*[Title/Abstract] OR adolescent*[Title/Abstract]
OR "Child"[Mesh] OR "Infant"[Mesh] OR "Adolescent"[Mesh] OR "Pediatrics"[Mesh]
)"""

        exposicao = """(
dermocosmetic*[Title/Abstract] OR dermo-cosmetic*[Title/Abstract] OR cosmeceutical*[Title/Abstract]
OR cosmetic*[Title/Abstract] OR "skin care"[Title/Abstract] OR "skin care product*"[Title/Abstract]
OR moisturizer*[Title/Abstract] OR moisturiser*[Title/Abstract] OR emollient*[Title/Abstract]
OR sunscreen*[Title/Abstract] OR "topical product*"[Title/Abstract]
OR "Cosmetics"[Mesh] OR "Skin Care"[Mesh] OR "Sunscreening Agents"[Mesh] OR "Emollients"[Mesh]
)"""

        desfecho = """(
adverse[Title/Abstract] OR harmful[Title/Abstract] OR toxicity[Title/Abstract] OR toxic*[Title/Abstract]
OR irritation[Title/Abstract] OR dermatitis[Title/Abstract] OR allergy[Title/Abstract] OR allergic[Title/Abstract]
OR hypersensitivity[Title/Abstract] OR "skin reaction*"[Title/Abstract] OR "adverse effect*"[Title/Abstract]
OR "Adverse Drug Reaction Reporting Systems"[Mesh] OR "Dermatitis"[Mesh] OR "Hypersensitivity"[Mesh]
)"""

        if "sistemática" in tipo_revisao.lower() or "systematic" in tipo_revisao.lower():
            estudo = """(
"systematic review"[Publication Type] OR "meta-analysis"[Publication Type]
OR "systematic review"[Title/Abstract] OR "meta-analysis"[Title/Abstract]
OR "evidence synthesis"[Title/Abstract]
)"""
        elif "integrativa" in tipo_revisao.lower():
            estudo = """(
"integrative review"[Title/Abstract] OR "literature review"[Title/Abstract]
OR "review"[Publication Type]
)"""
        else:
            estudo = """(
review[Title/Abstract] OR "observational study"[Title/Abstract]
OR cohort[Title/Abstract] OR "cross-sectional"[Title/Abstract]
)"""

        exclusao = """NOT (
animals[Mesh] NOT humans[Mesh]
)"""

        return f"""{populacao}
AND
{exposicao}
AND
{desfecho}
AND
{estudo}
{exclusao}"""

    # Fallback genérico para outros temas
    termos = tema.replace(",", " ").split()
    termos = [t.strip() for t in termos if len(t.strip()) > 3]

    livres = " OR ".join([f'"{t}"[Title/Abstract]' for t in termos])

    return f"""(
{livres}
)
AND
(
"systematic review"[Title/Abstract] OR "meta-analysis"[Title/Abstract] OR review[Publication Type]
)
NOT
(
animals[Mesh] NOT humans[Mesh]
)"""
