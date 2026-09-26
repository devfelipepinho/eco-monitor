# Eco Monitor

Projeto prático integrador para capturar, tratar, armazenar e analisar dados ambientais simulados, utilizando Python, Pandas e SQLite de forma simples e didática.

## Objetivo

O projeto implementa um pipeline básico de dados com foco em treinamento em Data Science. A fonte é um JSON fictício de monitoramento ambiental, o armazenamento é feito em SQLite e as análises estatísticas são executadas em Python.

## Tecnologias utilizadas

- Python 3.10+
- Pandas
- Matplotlib
- SQLite
- python-dotenv
- Pytest

## Estrutura do projeto

```
eco-monitor/
├── data/
│   ├── raw/
│   │   └── dados_monitoramento.json
│   └── processed/
├── reports/
├── src/
│   ├── analytics/
│   │   ├── stats.py
│   │   └── visualizacoes.py
│   ├── database/
│   │   └── sqlite_db.py
│   └── ingestion/
│       └── load_data.py
├── tests/
│   └── test_stats.py
├── conftest.py
├── .env.example
├── .gitignore
├── main.py
├── README.md
└── requirements.txt
```

## Regras adotadas

- Banco de dados SQLite.
- JSON fictício como fonte dos dados.
- Colunas do banco em português.
- Implementação simples, linear e adequada a ambiente não avançado.
- Remoção do campo `operador` antes da persistência, como medida simples de governança/LGPD.
- Cada execução limpa o banco e a pasta `reports/` antes de gerar novos resultados.

## Pré-requisitos

- Python 3.10 ou superior instalado e acessível via terminal.
- Git (para clonar o repositório).

## Como configurar

Clone o repositório e entre na pasta:

```bash
git clone https://github.com/devfelipepinho/eco-monitor.git
cd eco-monitor
```

Crie e ative o ambiente virtual:

```bash
# macOS / Linux
python3 -m venv .venv
source .venv/bin/activate

# Windows
python -m venv .venv
.venv\Scripts\activate
```

Quando ativo, o terminal passa a exibir `(.venv)` no início da linha.

Instale as dependências:

```bash
pip install -r requirements.txt
```

Crie o arquivo `.env` a partir do modelo:

```bash
cp .env.example .env
```

O `.env` usa apenas caminhos relativos — nenhuma configuração de máquina é necessária:

```env
CAMINHO_JSON=data/raw/dados_monitoramento.json
CAMINHO_BANCO=eco_monitor.db
DATA_INICIAL=2026-01-01
DATA_FINAL=2026-01-08
```

## Executar o pipeline

Com o ambiente virtual ativo, dentro da pasta `eco-monitor`:

```bash
python main.py
```

O pipeline sempre limpa os resultados anteriores antes de gerar novos. Não é necessário apagar nada manualmente entre execuções.

## Saídas esperadas

Após a execução, o projeto gera:

| Arquivo | Descrição |
|---|---|
| `eco_monitor.db` | Banco SQLite populado |
| `data/processed/estacoes_tratadas.csv` | Estações tratadas e anonimizadas |
| `data/processed/leituras_tratadas.csv` | Leituras com nulos preenchidos |
| `reports/relatorio_analitico.txt` | Médias, estatísticas e outliers por parâmetro |
| `reports/grafico_*.png` | Gráfico de curvas + desvio padrão por estação |

## Testes

Com o ambiente virtual ativo:

```bash
pytest
```

## Observações

Este projeto foi mantido propositalmente simples para fins de prática acadêmica. Ele evita arquitetura avançada, serviços externos e otimizações complexas, priorizando clareza, organização e aderência ao enunciado.
