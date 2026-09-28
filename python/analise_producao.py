from pathlib import Path

import pandas as pd


# ============================================================
# 1. CONFIGURAÇÃO DE DIRETÓRIOS
# ============================================================

base_dir = Path(__file__).resolve().parent.parent

dados_dir = base_dir / "dados"
processados_dir = base_dir / "dados_processados"

processados_dir.mkdir(exist_ok=True)


def localizar_csv(nome_arquivo):
    """Localiza um CSV em dados sem depender de maiusculas/minusculas."""
    caminho_direto = dados_dir / nome_arquivo

    if caminho_direto.is_file():
        return caminho_direto

    nome_normalizado = nome_arquivo.casefold()

    for caminho in dados_dir.glob("*.csv"):
        if caminho.name.casefold() == nome_normalizado:
            return caminho

    arquivos_disponiveis = sorted(
        caminho.name for caminho in dados_dir.glob("*.csv")
    )

    raise FileNotFoundError(
        f"Arquivo CSV nao encontrado: {nome_arquivo}. "
        f"Pasta pesquisada: {dados_dir}. "
        f"Arquivos disponiveis: {arquivos_disponiveis}"
    )


# ============================================================
# 2. FUNÇÕES DE LIMPEZA
# ============================================================

def limpar_numero(valor):

    if pd.isna(valor):
        return None

    texto = str(valor).strip()

    if texto == "":
        return None

    texto = texto.replace(".", "")
    texto = texto.replace("%", "")
    texto = texto.replace(" ", "")
    texto = texto.replace(",", ".")

    try:
        return float(texto)

    except ValueError:
        return None


def limpar_percentual(valor):

    numero = limpar_numero(valor)

    if numero is None:
        return None

    return numero / 100 if numero > 1 else numero


# ============================================================
# 3. LEITURA DOS DADOS
# ============================================================

producao = pd.read_csv(
    localizar_csv("Producao.csv")
)

maquinas = pd.read_csv(
    localizar_csv("Maquinas.csv")
)

produtos = pd.read_csv(
    localizar_csv("Produtos.csv")
)

perdas = pd.read_csv(
    localizar_csv("Perdas.csv")
)


# ============================================================
# 4. PADRONIZAÇÃO DOS NOMES DAS COLUNAS
# ============================================================

for df in [
    producao,
    maquinas,
    produtos,
    perdas
]:

    df.columns = [
        col.strip()
        for col in df.columns
    ]


# ============================================================
# 5. LIMPEZA DA TABELA DE PRODUÇÃO
# ============================================================

producao["Data"] = pd.to_datetime(
    producao["Data"],
    dayfirst=True,
    errors="coerce"
)


for coluna in [
    "Meta_Kg",
    "Produzido_Kg",
    "Perda_Kg",
    "Horas_Producao"
]:

    producao[coluna] = (
        producao[coluna]
        .apply(limpar_numero)
    )


producao["Eficiencia"] = (
    producao["Eficiencia"]
    .apply(limpar_percentual)
)


producao["Percentual_Perdas"] = (
    producao["Percentual_Perdas"]
    .apply(limpar_percentual)
)


# ============================================================
# 6. LIMPEZA DA TABELA DE PERDAS
# ============================================================

perdas["Quantidade_Kg"] = (
    perdas["Quantidade_Kg"]
    .apply(limpar_numero)
)


perdas["Data"] = pd.to_datetime(
    perdas["Data"],
    dayfirst=True,
    errors="coerce"
)


# ============================================================
# 7. VALIDAÇÃO DE QUALIDADE DOS DADOS
# ============================================================

problemas = []


# ---------- Datas ----------

linhas_nulas_data = (
    producao["Data"]
    .isna()
    .sum()
)


if linhas_nulas_data > 0:

    problemas.append(
        f"Produção: "
        f"{linhas_nulas_data} "
        f"data(s) inválida(s) ou vazia(s)."
    )


# ---------- Metas ----------

linhas_nulas_meta = (
    producao["Meta_Kg"]
    .isna()
    .sum()
)


if linhas_nulas_meta > 0:

    problemas.append(
        f"Produção: "
        f"{linhas_nulas_meta} "
        f"meta(s) vazia(s)."
    )


# ---------- Produção ----------

linhas_nulas_producao = (
    producao["Produzido_Kg"]
    .isna()
    .sum()
)


if linhas_nulas_producao > 0:

    problemas.append(
        f"Produção: "
        f"{linhas_nulas_producao} "
        f"produção(ões) vazia(s)."
    )


# ---------- Perdas ----------

linhas_nulas_perda = (
    producao["Perda_Kg"]
    .isna()
    .sum()
)


if linhas_nulas_perda > 0:

    problemas.append(
        f"Produção: "
        f"{linhas_nulas_perda} "
        f"perda(s) vazia(s)."
    )


# ---------- Valores negativos ----------

for coluna in [
    "Meta_Kg",
    "Produzido_Kg",
    "Perda_Kg",
    "Horas_Producao"
]:

    quantidade_negativa = (
        producao[coluna] < 0
    ).sum()


    if quantidade_negativa > 0:

        problemas.append(
            f"Produção: "
            f"{quantidade_negativa} "
            f"valor(es) negativo(s) "
            f"em {coluna}."
        )


# ---------- Meta igual a zero ----------

meta_zero = (
    producao["Meta_Kg"] == 0
).sum()


if meta_zero > 0:

    problemas.append(
        f"Produção: "
        f"{meta_zero} "
        f"registro(s) com meta igual a zero."
    )


# ---------- Duplicidades ----------

duplicados_producao = (
    producao
    .duplicated()
    .sum()
)


if duplicados_producao > 0:

    problemas.append(
        f"Produção: "
        f"{duplicados_producao} "
        f"registro(s) duplicado(s)."
    )


duplicados_perdas = (
    perdas
    .duplicated()
    .sum()
)


if duplicados_perdas > 0:

    problemas.append(
        f"Perdas: "
        f"{duplicados_perdas} "
        f"registro(s) duplicado(s)."
    )


# ---------- Integridade de máquinas ----------

maquinas_cadastradas = set(
    maquinas["Maquina"]
    .dropna()
)


maquinas_producao = set(
    producao["Maquina"]
    .dropna()
)


maquinas_sem_cadastro = (
    maquinas_producao
    -
    maquinas_cadastradas
)


if maquinas_sem_cadastro:

    problemas.append(
        "Máquinas sem cadastro: "
        +
        ", ".join(
            sorted(maquinas_sem_cadastro)
        )
    )


# ---------- Integridade de produtos ----------

produtos_cadastrados = set(
    produtos["Produto"]
    .dropna()
)


produtos_producao = set(
    producao["Produto"]
    .dropna()
)


produtos_sem_cadastro = (
    produtos_producao
    -
    produtos_cadastrados
)


if produtos_sem_cadastro:

    problemas.append(
        "Produtos sem cadastro: "
        +
        ", ".join(
            sorted(produtos_sem_cadastro)
        )
    )


# ============================================================
# 8. CÁLCULO DOS INDICADORES GERAIS
# ============================================================

meta_total = (
    producao["Meta_Kg"]
    .sum()
)


produzido_total = (
    producao["Produzido_Kg"]
    .sum()
)


perda_total_producao = (
    producao["Perda_Kg"]
    .sum()
)


perda_total_detalhada = (
    perdas["Quantidade_Kg"]
    .sum()
)


if meta_total:

    indicador_meta = (
        produzido_total
        /
        meta_total
    ) * 100

else:

    indicador_meta = 0


if producao["Eficiencia"].notna().any():

    eficiencia_media = (
        producao["Eficiencia"]
        .mean()
    ) * 100

else:

    eficiencia_media = 0


if produzido_total:

    percentual_perdas = (
        perda_total_producao
        /
        produzido_total
    ) * 100

else:

    percentual_perdas = 0


# ---------- Diferença de perdas ----------

diferenca_perdas = (
    perda_total_producao
    -
    perda_total_detalhada
)


if diferenca_perdas != 0:

    problemas.append(
        f"Divergência de perdas: "
        f"{round(diferenca_perdas, 2)} kg "
        f"entre produção e perdas detalhadas."
    )


# ============================================================
# 9. ANÁLISES GERAIS
# ============================================================

perdas_por_motivo = (
    perdas
    .groupby("Motivo")["Quantidade_Kg"]
    .sum()
    .sort_values(
        ascending=False
    )
)


producao_por_maquina = (
    producao
    .groupby("Maquina")["Produzido_Kg"]
    .sum()
    .sort_values(
        ascending=False
    )
)


maquina_mais_produtiva = (
    producao_por_maquina
    .head(1)
)


producao_por_produto = (
    producao
    .groupby("Produto")["Produzido_Kg"]
    .sum()
    .sort_values(
        ascending=False
    )
)


# ============================================================
# 9.1 COMPARAÇÃO DE PERDAS POR MÁQUINA
# ============================================================

perda_producao_por_maquina = (
    producao
    .groupby("Maquina")["Perda_Kg"]
    .sum()
)


perda_detalhada_por_maquina = (
    perdas
    .groupby("Maquina")["Quantidade_Kg"]
    .sum()
)


comparacao_perdas = pd.concat(
    [
        perda_producao_por_maquina,
        perda_detalhada_por_maquina
    ],
    axis=1
)


comparacao_perdas.columns = [
    "Perda_Producao_Kg",
    "Perda_Detalhada_Kg"
]


comparacao_perdas["Diferenca_Kg"] = (
    comparacao_perdas["Perda_Producao_Kg"]
    -
    comparacao_perdas["Perda_Detalhada_Kg"]
)


comparacao_perdas = (
    comparacao_perdas
    .fillna(0)
)


comparacao_perdas = (
    comparacao_perdas
    .sort_values(
        by="Diferenca_Kg",
        ascending=False
    )
)


# ============================================================
# 9.2 REGRAS DE NEGÓCIO POR MÁQUINA
# ============================================================

indicadores_maquinas = (
    producao
    .groupby("Maquina")
    .agg(
        Meta_Total_Kg=(
            "Meta_Kg",
            "sum"
        ),

        Produzido_Total_Kg=(
            "Produzido_Kg",
            "sum"
        ),

        Perda_Total_Kg=(
            "Perda_Kg",
            "sum"
        ),

        Horas_Producao=(
            "Horas_Producao",
            "sum"
        ),

        Eficiencia_Media=(
            "Eficiencia",
            "mean"
        )
    )
    .reset_index()
)


# ---------- Cumprimento da meta ----------

indicadores_maquinas[
    "Cumprimento_Meta_Pct"
] = (

    indicadores_maquinas[
        "Produzido_Total_Kg"
    ]

    /

    indicadores_maquinas[
        "Meta_Total_Kg"
    ]

) * 100


# ---------- Percentual de perdas ----------

indicadores_maquinas[
    "Percentual_Perdas_Pct"
] = (

    indicadores_maquinas[
        "Perda_Total_Kg"
    ]

    /

    indicadores_maquinas[
        "Produzido_Total_Kg"
    ]

) * 100


# ---------- Eficiência em percentual ----------

indicadores_maquinas[
    "Eficiencia_Media_Pct"
] = (
    indicadores_maquinas[
        "Eficiencia_Media"
    ] * 100
)


# ---------- Status da meta ----------

indicadores_maquinas[
    "Status_Meta"
] = indicadores_maquinas[
    "Cumprimento_Meta_Pct"
].apply(
    lambda x:
    "Atingiu"
    if x >= 100
    else "Abaixo"
)


# ---------- Status operacional ----------

def definir_status_operacional(linha):

    cumprimento = (
        linha["Cumprimento_Meta_Pct"]
    )

    eficiencia = (
        linha["Eficiencia_Media_Pct"]
    )

    perdas_pct = (
        linha["Percentual_Perdas_Pct"]
    )


    if (
        cumprimento >= 100
        and
        eficiencia >= 95
        and
        perdas_pct <= 3
    ):

        return "Normal"


    elif (
        cumprimento >= 90
        and
        eficiencia >= 90
        and
        perdas_pct <= 5
    ):

        return "Atenção"


    else:

        return "Crítico"


indicadores_maquinas[
    "Status_Operacional"
] = indicadores_maquinas.apply(
    definir_status_operacional,
    axis=1
)


# ---------- Ranking de produção ----------

indicadores_maquinas[
    "Ranking_Producao"
] = (
    indicadores_maquinas[
        "Produzido_Total_Kg"
    ]
    .rank(
        ascending=False,
        method="dense"
    )
    .astype(int)
)


# ---------- Ordenação ----------

indicadores_maquinas = (
    indicadores_maquinas
    .sort_values(
        by="Ranking_Producao"
    )
)


# ---------- Arredondamento ----------

colunas_numericas = [
    "Meta_Total_Kg",
    "Produzido_Total_Kg",
    "Perda_Total_Kg",
    "Horas_Producao",
    "Cumprimento_Meta_Pct",
    "Percentual_Perdas_Pct",
    "Eficiencia_Media_Pct"
]


indicadores_maquinas[
    colunas_numericas
] = indicadores_maquinas[
    colunas_numericas
].round(2)


# ============================================================
# 10. TABELA DE QUALIDADE
# ============================================================

if problemas:

    status_qualidade = "ATENÇÃO"

else:

    status_qualidade = "OK"


qualidade = pd.DataFrame(
    {
        "Indicador": [

            "Status geral da qualidade",

            "Registros produção",

            "Registros perdas",

            "Duplicados produção",

            "Duplicados perdas",

            "Máquinas sem cadastro",

            "Produtos sem cadastro",

            "Perda produção (kg)",

            "Perda detalhada (kg)",

            "Diferença de perdas (kg)",
        ],

        "Valor": [

            status_qualidade,

            len(producao),

            len(perdas),

            duplicados_producao,

            duplicados_perdas,

            len(maquinas_sem_cadastro),

            len(produtos_sem_cadastro),

            round(
                perda_total_producao,
                2
            ),

            round(
                perda_total_detalhada,
                2
            ),

            round(
                diferenca_perdas,
                2
            ),
        ],
    }
)


# ============================================================
# 11. RESUMO INDUSTRIAL
# ============================================================

resumo = pd.DataFrame(
    {
        "Indicador": [

            "Meta total (kg)",

            "Produzido total (kg)",

            "Perdas totais (kg)",

            "% cumprimento da meta",

            "Eficiência média (%)",

            "% perdas sobre produção",

            "Máquina com maior produção",

            "Produto com maior produção",
        ],

        "Valor": [

            round(
                meta_total,
                2
            ),

            round(
                produzido_total,
                2
            ),

            round(
                perda_total_producao,
                2
            ),

            round(
                indicador_meta,
                2
            ),

            round(
                eficiencia_media,
                2
            ),

            round(
                percentual_perdas,
                2
            ),

            (
                f"{maquina_mais_produtiva.index[0]} "
                f"("
                f"{round(maquina_mais_produtiva.iloc[0], 2)} "
                f"kg)"
            ),

            (
                f"{producao_por_produto.index[0]} "
                f"("
                f"{round(producao_por_produto.iloc[0], 2)} "
                f"kg)"
            ),
        ],
    }
)


# ============================================================
# 12. EXPORTAÇÃO DOS DADOS PROCESSADOS
# ============================================================

producao.to_csv(
    processados_dir /
    "producao_tratada.csv",
    index=False
)


perdas.to_csv(
    processados_dir /
    "perdas_tratadas.csv",
    index=False
)


resumo.to_csv(
    processados_dir /
    "resumo_industrial.csv",
    index=False
)


qualidade.to_csv(
    processados_dir /
    "qualidade_dados.csv",
    index=False
)


comparacao_perdas.to_csv(
    processados_dir /
    "comparacao_perdas.csv"
)


indicadores_maquinas.to_csv(
    processados_dir /
    "indicadores_maquinas.csv",
    index=False
)


# ============================================================
# 13. RELATÓRIO NO TERMINAL
# ============================================================

print("\n")

print("=" * 60)

print(
    "        ETL - DASHBOARD INDUSTRIAL"
)

print("=" * 60)


print("\n=== RESUMO INDUSTRIAL ===")

print(
    resumo.to_string(
        index=False
    )
)


print("\n=== QUALIDADE DOS DADOS ===")

print(
    qualidade.to_string(
        index=False
    )
)


print("\n=== PRODUÇÃO POR MÁQUINA ===")

print(
    producao_por_maquina
)


print("\n=== PRODUÇÃO POR PRODUTO ===")

print(
    producao_por_produto
)


print("\n=== PERDAS POR MOTIVO ===")

print(
    perdas_por_motivo
)


print(
    "\n=== COMPARAÇÃO DE PERDAS POR MÁQUINA ==="
)

print(
    comparacao_perdas
)


print(
    "\n=== INDICADORES POR MÁQUINA ==="
)

print(
    indicadores_maquinas.to_string(
        index=False
    )
)


if problemas:

    print(
        "\n=== ALERTAS DE QUALIDADE ==="
    )

    for problema in problemas:

        print(
            f"- {problema}"
        )

else:

    print(
        "\n=== QUALIDADE ==="
    )

    print(
        "Nenhum problema crítico encontrado."
    )


print(
    "\n=== ARQUIVOS PROCESSADOS ==="
)


print(
    processados_dir /
    "producao_tratada.csv"
)


print(
    processados_dir /
    "perdas_tratadas.csv"
)


print(
    processados_dir /
    "resumo_industrial.csv"
)


print(
    processados_dir /
    "qualidade_dados.csv"
)


print(
    processados_dir /
    "comparacao_perdas.csv"
)


print(
    processados_dir /
    "indicadores_maquinas.csv"
)


print(
    "\nETL concluído com sucesso."
)