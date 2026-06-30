from graphviz import Digraph
from pathlib import Path


def gerar_fluxograma_prisma(
    total_identificados,
    total_sem_duplicatas,
    total_apos_similaridade,
    caminho_base="outputs/figures/fluxograma_prisma"
):
    Path("outputs/figures").mkdir(parents=True, exist_ok=True)

    dot = Digraph(comment="Fluxograma PRISMA")
    dot.attr(rankdir="TB")
    dot.attr("node", shape="box", style="rounded,filled", fillcolor="white", fontname="Arial")

    removidos = total_identificados - total_sem_duplicatas
    excluidos_similaridade = total_sem_duplicatas - total_apos_similaridade

    dot.node("A", f"Registros identificados\\nTotal = {total_identificados}")
    dot.node("B", f"Registros após remoção de duplicatas\\nTotal = {total_sem_duplicatas}")
    dot.node("C", f"Registros removidos como duplicatas\\nTotal = {removidos}")
    dot.node("D", f"Registros avaliados por similaridade semântica\\nTotal = {total_sem_duplicatas}")
    dot.node("E", f"Registros excluídos por baixa similaridade\\nTotal = {excluidos_similaridade}")
    dot.node("F", f"Estudos incluídos na síntese final\\nTotal = {total_apos_similaridade}")

    dot.edge("A", "B")
    dot.edge("A", "C")
    dot.edge("B", "D")
    dot.edge("D", "E")
    dot.edge("D", "F")

    svg_path = dot.render(caminho_base, format="svg", cleanup=True)
    pdf_path = dot.render(caminho_base, format="pdf", cleanup=True)

    return svg_path, pdf_path
