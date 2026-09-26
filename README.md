# Eco Monitor

Projeto prático integrador para capturar, tratar, armazenar e analisar dados ambientais simulados, utilizando Python, Pandas e SQLite de forma simples e didática.

## Objetivo

O projeto implementa um pipeline básico de dados com foco em treinamento em Data Science. A fonte é um JSON fictício de monitoramento ambiental, o armazenamento é feito em SQLite e as análises estatísticas são executadas em Python.

## Tecnologias utilizadas

- Python
- Pandas
- SQLite
- python-dotenv
- Pytest
- Matplotlib (dependência prevista para expansão de gráficos simples)

## Estrutura do projeto

```bash
eco-monitor/
├── data/
│   ├── raw/
│   │   └── dados_monitoramento.json
│   └── processed/
├── reports/
├── src/
│   ├── analytics/
│   │   └── stats.py
│   ├── database/
│   │   └── sqlite_db.py
│   └── ingestion/
│       └── load_data.py
├── tests/
│   └── test_stats.py
├── .env.example
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```

## Regras adotadas

- Banco de dados SQLite.
- JSON fictício como fonte dos dados.
- Colunas do banco em português.
- Implementação simples, linear e adequada a ambiente não avançado.
- Remoção do campo `operador` antes da persistência, como medida simples de governança/LGPD.

## Ordem correta de execução

1. Criar o ambiente virtual.
2. Ativar o ambiente virtual.
3. Instalar as dependências.
4. Criar o arquivo `.env`.
5. Executar o pipeline.

## Como criar a env do projeto

Entre na pasta do projeto:

```bash
cd "/Volumes/HD/GitHub/eco-monitor"
```

Crie o ambiente virtual:

```bash
python3 -m venv .venv
```

Ative o ambiente virtual no macOS/Linux:

```bash
source .venv/bin/activate
```

Se estiver no Windows, use:

```bash
.venv\Scripts\activate
```

Quando der certo, o terminal normalmente passa a mostrar algo como `(.venv)` no começo da linha.

## Instalar dependências

Com a env ativada, rode:

```bash
pip install -r requirements.txt
```

## Criar o arquivo .env

Depois da instalação, crie o arquivo `.env` a partir do modelo:

```bash
cp .env.example .env
```

O conteúdo esperado do `.env` é:

```env
CAMINHO_JSON=data/raw/dados_monitoramento.json
CAMINHO_BANCO=eco_monitor.db
```

## Executar o pipeline

Depois disso, execute:

```bash
python main.py
```

## Saídas esperadas

Após a execução, o projeto deve gerar:

- `eco_monitor.db`: banco SQLite populado.
- `data/processed/estacoes_tratadas.csv`: estações tratadas e anonimizadas.
- `data/processed/leituras_tratadas.csv`: leituras tratadas.
- `reports/relatorio_analitico.txt`: relatório com médias, estatísticas básicas e outliers.

## Testes

Para rodar os testes unitários:

```bash
pytest
```

## Observações

Este projeto foi mantido propositalmente simples para fins de prática acadêmica. Ele evita arquitetura avançada, serviços externos e otimizações complexas, priorizando clareza, organização e aderência ao enunciado.
