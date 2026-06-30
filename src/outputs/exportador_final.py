try:
    from exportacao_prisma_elegante import (
        exportar_master_prisma,
        exportar_excel_master,
        exportar_word_tabela_artigo,
    )
except ImportError:
    from src.exportacao_prisma_elegante import (
        exportar_master_prisma,
        exportar_excel_master,
        exportar_word_tabela_artigo,
    )
