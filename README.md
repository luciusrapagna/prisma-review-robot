# PRISMA Review Robot

Robo em Python para apoiar revisoes bibliograficas do tipo PRISMA, revisao sistematica, revisao integrativa, revisao narrativa e revisao de escopo.

## Objetivo

Automatizar etapas iniciais de uma revisao bibliografica cientifica, permitindo que o usuario informe parametros de busca, descritores, bases de dados, periodo de publicacao e criterios de inclusao/exclusao.

## Funcionalidades previstas

- Insercao de parametros da revisao
- Busca bibliografica automatizada em PubMed, Crossref, SciELO e LILACS/BVS
- Geracao automatica de queries booleanas com sinonimos
- Organizacao dos artigos encontrados
- Remocao de duplicatas
- Ranking semantico por similaridade de texto
- Geracao de tabela em Excel
- Geracao de arquivo de referencias para Zotero
- Geracao de resumo metodologico
- Geracao de descricao para figura PRISMA
- Organizacao dos resultados em pastas de projeto numeradas
- Exportacao dos dados para uso em artigos cientificos

## Estrutura do projeto

```text
PRISMA-Review-Robot/
  src/
    __init__.py
    main.py
    config.py
    buscador.py
    figuras.py
    relatorios.py
    referencias.py
    triagem.py
    buscadores/
      pubmed.py
      crossref.py
      scielo.py
      lilacs.py
    ia/
      ranking_semantico.py
      gerador_booleano.py
    outputs/
      word_writer.py
    prisma/
      duplicates.py

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

```powershell
# Windows (PowerShell)
$env:HF_TOKEN = "seu_token_aqui"
```

```cmd
REM Windows (Command Prompt)
set HF_TOKEN=seu_token_aqui
```

```bash
# Linux/Mac
export HF_TOKEN=seu_token_aqui
```

Ou adicione permanentemente ao seu sistema operacional.

## Uso

Execute o robo pelo terminal a partir da pasta do projeto:

```bash
python src\main.py
```

> Opcional: se preferir, voce pode executar como modulo Python:
>
> ```bash
> python -m src.main
> ```

O programa ira solicitar:

- Tema da revisao
- Ano inicial e ano final
- Escolha entre query manual ou gerador automatico
- Numero maximo de artigos por base
- Tipo de revisao desejada

## Fluxo de uso rapido

1. Execute `python src\main.py`.
2. Informe o tema e o periodo de publicacao.
3. Escolha entre gerar a query automaticamente ou inserir a query booleana manualmente.
4. Defina o maximo de artigos por base.
5. Aguarde a busca, consolidacao, remocao de duplicatas e ranking semantico.
6. Verifique as pastas do projeto dentro de `projetos/projeto X`.

## Saida

Os resultados do projeto são organizados em pastas numeradas dentro de `projetos/`, por exemplo:

- `projetos/projeto 1/outputs/tables`
- `projetos/projeto 1/outputs/figures`
- `projetos/projeto 1/outputs/references`
- `projetos/projeto 1/data/raw`
- `projetos/projeto 1/data/processed`
- `projetos/projeto 1/logs`

O arquivo Word gerado é exibido no final da execução com o caminho completo.

## Dependencias principais

O projeto usa as seguintes bibliotecas Python:

- `pandas`
- `openpyxl`
- `requests`
- `python-docx`
- `sentence-transformers`
- `scikit-learn`

Para a lista completa, consulte `requirements.txt`.

## Observacoes

- A implementacao atual realiza busca em PubMed, Crossref, SciELO e LILACS/BVS.
- Existe um gerador automatico de queries booleanas em `src/ia/gerador_booleano.py`.
- Os resultados sao salvos em pastas de projeto numeradas automaticamente.
- Voce pode adaptar o robo para outras bases de dados ou formatos de exportacao.

## Contribuicoes

Contribuicoes sao bem-vindas. Abra uma issue ou envie um pull request com sugestoes de melhorias.
