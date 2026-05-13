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
```

## Instalação

1. Clone o repositório:

```bash
git clone https://github.com/luciusrapagna/prisma-review-robot.git
cd prisma-review-robot
```

2. Crie e ative um ambiente virtual Python:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

## Uso

Execute o robô pelo terminal:

```bash
python src\main.py
```

O programa irá solicitar:

- Tema da revisão
- Ano inicial e ano final
- Busca booleana para PubMed
- Número máximo de artigos
- Tipo de revisão desejada

Ao final, os resultados serão salvos em:

- `outputs/tables/parametros_revisao.xlsx`
- `outputs/figures/descricao_figura_prisma.txt`
- `outputs/references/referencias_pubmed.ris`

## Dependências principais

O projeto usa as seguintes bibliotecas Python:

- `pandas`
- `openpyxl`
- `requests`
- `python-docx`

Para a lista completa, consulte `requirements.txt`.

## Observações

- A implementação atual realiza busca no PubMed via `src/buscadores/pubmed.py`.
- A saída pode ser usada como base para gerar tabelas, gráficos e fluxogramas PRISMA.
- Você pode adaptar o robô para outras bases de dados ou formatos de exportação.

## Contribuições

Contribuições são bem-vindas. Abra uma issue ou envie um pull request com sugestões de melhorias.
