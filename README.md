# PRISMA Review Robot

Robô em Python para apoiar revisões bibliográficas do tipo PRISMA, revisão sistemática, revisão integrativa, revisão narrativa e revisão de escopo.

## Objetivo

Automatizar etapas iniciais de uma revisão bibliográfica científica, permitindo que o usuário informe parâmetros de busca, descritores, bases de dados, período de publicação e critérios de inclusão/exclusão.

## Funcionalidades previstas

- Inserção de parâmetros da revisão
- Busca bibliográfica automatizada
- Organização dos artigos encontrados
- Remoção de duplicatas
- Triagem inicial por título e resumo
- Geração de tabela em Excel
- Geração de arquivo de referências para Zotero
- Geração de resumo metodológico
- Geração de descrição para figura PRISMA
- Organização dos resultados em pastas
- Exportação dos dados para uso em artigos científicos

## Estrutura do projeto

```text
PRISMA-Review-Robot/
│
├── src/
│   ├── main.py
│   ├── config.py
│   ├── buscador.py
│   ├── triagem.py
│   ├── relatorios.py
│   ├── referencias.py
│   └── figuras.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── outputs/
│   ├── tables/
│   ├── figures/
│   └── references/
│
├── docs-reference/
├── prompts/
├── logs/
├── requirements.txt
├── .gitignore
└── README.md