# Dashboard Industrial — Análise de Produção e Perdas

## Objetivo

Este projeto trata e analisa dados de produção e perdas industriais. O ETL em Python lê arquivos CSV, calcula indicadores e verificações de qualidade e grava resultados em CSVs para análise.

O relatório Power BI é uma camada separada de visualização. O script Python não carrega nem atualiza o PostgreSQL.

## Tecnologias e responsabilidades

- **Python** executa o ETL e as regras de análise.
- **Pandas** lê, transforma, agrupa e exporta dados tabulares.
- **NumPy** é usado em cálculos com valores ausentes e divergências percentuais.
- **PostgreSQL** é o banco local consultado pelo relatório Power BI. A conexão informada para o relatório é `PostgreSQL.Database("localhost:5432", "dashboard_industrial")`.
- **Power BI** apresenta relatórios e indicadores a partir da fonte configurada.

A preparação do banco, a definição de tabelas e o processo de carga precisam ser documentados separadamente. Este repositório não documenta nem executa uma carga automática do PostgreSQL.

## Estrutura do repositório

```text
Projeto_Dashboard_Industrial/
├── dados/                    # CSVs de entrada usados pelo ETL
├── dados_processados/        # CSVs de saída do ETL
├── python/
│   └── analise_producao.py   # script principal
├── powerbi/                  # arquivos de relatório Power BI
├── documentacao/             # documentação complementar
├── requirements.txt          # dependências Python do ETL
└── README.MD
```

Há também arquivos `.pbix` na raiz. O repositório contém mais de uma versão de relatório; confirme qual arquivo é apropriado antes de publicar ou atualizar um dashboard.

O script encontra a raiz do projeto a partir do caminho do próprio arquivo. Assim, os caminhos de `dados/` e `dados_processados/` não dependem do diretório atual do terminal. Os CSVs de entrada devem ficar em `dados/`; CSVs que existam em `python/` não são lidos pelo ETL.

## Entradas do ETL

O script lê estes quatro arquivos de `dados/` (a busca de nomes não diferencia maiúsculas de minúsculas):

- `dados/Producao.csv`
- `dados/Maquinas.csv`
- `dados/Produtos.csv`
- `dados/Perdas.csv`

## Ambiente Python no Windows PowerShell

Execute os comandos a partir da raiz do repositório:

```powershell
python --version
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python python/analise_producao.py
```

Se a ativação for bloqueada pela política de execução do PowerShell, permita scripts apenas nesta sessão e tente ativar novamente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

As versões fixadas em `requirements.txt` correspondem às versões encontradas no ambiente virtual local no momento desta documentação. São uma referência para reproduzir esse ambiente, não uma declaração de que o ETL foi executado ou validado em uma instalação limpa. O projeto não declara uma matriz mais ampla de versões testadas.

## Execução e arquivos gerados

A execução de `python python/analise_producao.py` processa os quatro CSVs de entrada e grava em `dados_processados/`:

- `maquinas_tratadas.csv`
- `produtos_tratados.csv`
- `producao_tratada.csv`
- `perdas_tratadas.csv`
- `resumo_industrial.csv`
- `qualidade_dados.csv`
- `comparacao_perdas.csv`
- `comparacao_perdas_data_maquina.csv`
- `indicadores_maquinas.csv`

**Atenção:** o ETL grava novamente nesses caminhos. Faça uma cópia dos resultados que deseja preservar antes de executar; os CSVs existentes em `dados_processados/` podem ser sobrescritos.

## Análises e verificações implementadas

O script calcula totais de meta, produção e perdas; percentual de cumprimento da meta; eficiência média; percentual de perdas sobre a produção; produção por máquina e produto; máquina e produto com maior produção; e perdas por motivo.

Os indicadores por máquina incluem meta, produção, perdas, horas, eficiência média, cumprimento da meta, percentual de perdas, status da meta, status operacional e ranking de produção. O status operacional é **Normal** quando o cumprimento é pelo menos 100%, a eficiência pelo menos 95% e as perdas no máximo 3%; é **Atenção** quando o cumprimento é pelo menos 90%, a eficiência pelo menos 90% e as perdas no máximo 5%; caso contrário, é **Crítico**.

A tabela de qualidade registra, entre outros itens:

- datas ausentes ou inválidas e campos ausentes de meta, produção e perda;
- contagem de valores numéricos negativos e registros com meta ou horas iguais a zero;
- linhas duplicadas em produção e perdas;
- máquinas e produtos da produção sem cadastro correspondente;
- diferenças entre percentuais de perdas informados e calculados;
- diferença entre perda registrada na produção e perda detalhada.

As perdas são comparadas no agregado por máquina e por combinação de data e máquina. A comparação por data/máquina classifica a combinação como conciliada quando a diferença absoluta é menor que `0,01 kg`; caso contrário, marca divergência. O status geral de qualidade considera os problemas que o código adiciona à lista de alertas.

Os arquivos de comparação atualmente disponíveis em `dados_processados/` apresentam divergências entre os valores de perdas. Investigue e concilie essas diferenças antes de considerar os resultados definitivos. O ETL recalcula os arquivos a partir das entradas atuais, mas não resolve por si só divergências na origem.

## PostgreSQL e Power BI

O ETL processa CSVs e grava CSVs; não conecta ao PostgreSQL e não atualiza o banco. O relatório Power BI utiliza a conexão local `localhost:5432` para o banco `dashboard_industrial`. Em outro computador, a instalação e configuração do PostgreSQL, a preparação e carga dos dados e as credenciais da conexão devem ser tratadas separadamente.

A documentação atual não especifica um procedimento reproduzível de criação e carga do banco. Não presuma que clonar o projeto ou executar o ETL prepare o PostgreSQL automaticamente. Não inclua senhas ou tokens no repositório.

## Limitações de validação

Os comandos acima documentam como executar o script, mas não declaram que a execução foi testada em uma instalação limpa. Valide os resultados e investigue os alertas de qualidade antes de usá-los como definitivos.
