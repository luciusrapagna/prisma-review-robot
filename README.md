# PRISMA Review Robot

Robo em Python para apoiar revisoes bibliograficas do tipo PRISMA, revisao sistematica, revisao integrativa, revisao narrativa e revisao de escopo.

## Objetivo

Automatizar etapas iniciais de uma revisao bibliografica cientifica, permitindo que o usuario informe parametros de busca, descritores, bases de dados, periodo de publicacao e criterios de inclusao/exclusao.

## Funcionalidades previstas

- Insercao de parametros da revisao
- Busca bibliografica automatizada
- Organizacao dos artigos encontrados
- Remocao de duplicatas
- Triagem inicial por titulo e resumo
- Geracao de tabela em Excel
- Geracao de arquivo de referencias para Zotero
- Geracao de resumo metodologico
- Geracao de descricao para figura PRISMA
- Organizacao dos resultados em pastas
- Exportacao dos dados para uso em artigos cientificos

## Estrutura do projeto

```text
PRISMA-Review-Robot/

 src/
    main.py
    config.py
    buscador.py
    triagem.py
    relatorios.py
    referencias.py
    figuras.py

 data/
    raw/
    processed/

 outputs/
    tables/
    figures/
    references/

 docs-reference/
 prompts/
 logs/
 requirements.txt
 .gitignore
 README.md
```

## Instalacao

1. Clone o repositorio:

```bash
git clone https://github.com/luciusrapagna/prisma-review-robot.git
cd prisma-review-robot
```

2. Crie e ative um ambiente virtual Python:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Instale as dependencias:

```bash
pip install -r requirements.txt
```

## Configuracao do Token do Hugging Face

O robo usa modelos de IA do Hugging Face para ranking semantico. Para evitar avisos de autenticacao e obter taxas de download mais altas:

1. Crie uma conta gratuita em [Hugging Face](https://huggingface.co/join)
2. Acesse [Configuracoes de Tokens](https://huggingface.co/settings/tokens)
3. Crie um novo token (tipo "Read")
4. Defina a variavel de ambiente:

```bash
# Windows (PowerShell)
$env:HF_TOKEN = "seu_token_aqui"

# Windows (Command Prompt)
set HF_TOKEN=seu_token_aqui

# Linux/Mac
export HF_TOKEN=seu_token_aqui
```

Ou adicione permanentemente ao seu sistema operacional.

## Uso

Execute o robo pelo terminal:

```bash
python src\main.py
```

O programa ira solicitar:

- Tema da revisao
- Ano inicial e ano final
- Busca booleana para PubMed
- Numero maximo de artigos
- Tipo de revisao desejada

Ao final, os resultados serao salvos em:

- `outputs/tables/parametros_revisao.xlsx`
- `outputs/figures/descricao_figura_prisma.txt`
- `outputs/references/referencias_pubmed.ris`

## Dependencias principais

O projeto usa as seguintes bibliotecas Python:

- `pandas`
- `openpyxl`
- `requests`
- `python-docx`

Para a lista completa, consulte `requirements.txt`.

## Observacoes

- A implementacao atual realiza busca no PubMed via `src/buscadores/pubmed.py`.
- A saida pode ser usada como base para gerar tabelas, graficos e fluxogramas PRISMA.
- Voce pode adaptar o robo para outras bases de dados ou formatos de exportacao.

## Contribuicoes

Contribuicoes sao bem-vindas. Abra uma issue ou envie um pull request com sugestoes de melhorias.
