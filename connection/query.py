class Query:
    def __init__(self, titulo, sql):
        self.titulo = titulo
        self.sql = sql
# Dicionário contendo consultas SQL pré-definidas
queries = {

    # Primeira consulta: Seleciona dados de receita para o ano de 2025
    "RECEITAS": Query(
     titulo="Receitas para o ano de 2025",
     sql="""
        
-- CTE que define manualmente as contas de receita a serem analisadas.
-- Para incluir ou remover contas, edite diretamente os SELECTs abaixo.
WITH ContasReceita AS (
    SELECT 'CSO - CONTR. SOCIAL ORDINÁRIA' AS Conta UNION ALL
    SELECT 'CSN - CONTR. SOCIAL NACIONAL' UNION ALL
    SELECT 'CONVÊNIOS com SEBRAE NA' UNION ALL
    SELECT 'CONVÊNIOS, SUBV. E AUXÍLIOS' UNION ALL
    SELECT 'CONTRATO INTERNO' UNION ALL
    SELECT 'EMPRESAS BENEFICIADAS' UNION ALL
    SELECT 'OUTRAS RECEITAS' UNION ALL
    SELECT 'APLICAÇÕES FINANCEIRAS'
),

-- CTE com os meses do ano a serem incluídos na análise.
-- Caso deseje outro ano, altere os valores de '2025-01' a '2025-12'.
Meses AS (
    SELECT '2025-01' AS AnoMes UNION ALL SELECT '2025-02' UNION ALL
    SELECT '2025-03' UNION ALL SELECT '2025-04' UNION ALL
    SELECT '2025-05' UNION ALL SELECT '2025-06' UNION ALL
    SELECT '2025-07' UNION ALL SELECT '2025-08' UNION ALL
    SELECT '2025-09' UNION ALL SELECT '2025-10' UNION ALL
    SELECT '2025-11' UNION ALL SELECT '2025-12'
),

-- CTE que forma uma grade completa de todas as combinações de conta e mês.
-- Isso garante que mesmo mês sem dados apareça no resultado.
GradeCompleta AS (
    SELECT m.AnoMes, c.Conta
    FROM Meses m
    CROSS JOIN ContasReceita c
),

-- CTE que agrega os valores reais das contas, por mês.
-- Altere o filtro TIPO para 'Despesa' se desejar mudar a análise.
BaseDados AS (
    SELECT 
        FORMAT(DATA, 'yyyy-MM') AS AnoMes,
        CASE 
            WHEN CONTA_FECHAMENTO = 'OUTRAS RECEITAS' AND COD_CONTA = '4.1.4.1.01.001' THEN 'APLICAÇÕES FINANCEIRAS'
            ELSE CONTA_FECHAMENTO
        END AS CONTA_FECHAMENTO,
        SUM(UNIFICAVALOR) AS Valor
    FROM FatoFechamento
    WHERE YEAR(DATA) = 2025 AND TIPO = 'Receita'
    GROUP BY FORMAT(DATA, 'yyyy-MM'),
             CASE 
                WHEN CONTA_FECHAMENTO = 'OUTRAS RECEITAS' AND COD_CONTA = '4.1.4.1.01.001' THEN 'APLICAÇÕES FINANCEIRAS'
                ELSE CONTA_FECHAMENTO
             END
),

-- Junta os dados reais com a grade para manter todos os meses e contas.
ComValores AS (
    SELECT 
        gc.AnoMes,
        gc.Conta,
        bd.Valor
    FROM GradeCompleta gc
    LEFT JOIN BaseDados bd
        ON gc.AnoMes = bd.AnoMes AND gc.Conta = bd.CONTA_FECHAMENTO
),

-- CTE que calcula o valor do mês anterior (ValorAnterior) para usar em previsões.
ComPrevisao AS (
    SELECT 
        cv.AnoMes,
        cv.Conta,
        cv.Valor,
        LAG(cv.Valor) OVER (PARTITION BY cv.Conta ORDER BY cv.AnoMes) AS ValorAnterior,
        CONVERT(DATE, cv.AnoMes + '-01') AS DataMes
    FROM ComValores cv
),

-- CTE que gera dois formatos: valor numérico e valor formatado
ComTexto AS (
    SELECT 
        cp.Conta,
        cp.AnoMes,
        FORMAT(DATEFROMPARTS(LEFT(cp.AnoMes,4), RIGHT(cp.AnoMes,2), 1), 'MMM', 'pt-br') AS MES_PT,
        CASE 
            WHEN cp.Valor IS NOT NULL THEN cp.Valor
            WHEN cp.ValorAnterior IS NOT NULL AND FORMAT(cp.DataMes, 'yyyyMM') = FORMAT(DATEADD(MONTH, -1, GETDATE()), 'yyyyMM')
                THEN cp.ValorAnterior
            ELSE NULL
        END AS ValorNumerico,
        CASE 
            WHEN cp.Valor IS NOT NULL THEN FORMAT(cp.Valor, 'C', 'pt-br')
            WHEN cp.ValorAnterior IS NOT NULL AND FORMAT(cp.DataMes, 'yyyyMM') = FORMAT(DATEADD(MONTH, -1, GETDATE()), 'yyyyMM')
                THEN FORMAT(cp.ValorAnterior, 'C', 'pt-br') + ' (P)'
            ELSE NULL
        END AS ValorFormatado
    FROM ComPrevisao cp
),

-- Pivot numérico: estrutura que organiza os valores por mês (colunas) e conta (linhas)
PivotNumerico AS (
    SELECT *
    FROM (
        SELECT 
            UPPER(Conta) AS Grupo,
            LOWER(MES_PT) AS Mes,
            ValorNumerico
        FROM ComTexto
        WHERE ValorNumerico IS NOT NULL
    ) AS src
    PIVOT (
        SUM(ValorNumerico)
        FOR Mes IN ([jan], [fev], [mar], [abr], [mai], [jun],
                    [jul], [ago], [set], [out], [nov], [dez])
    ) AS p
),

-- Pivot formatado: organiza os textos já formatados para exibição final
PivotFormatado AS (
    SELECT *
    FROM (
        SELECT 
            UPPER(Conta) AS Grupo,
            LOWER(MES_PT) AS Mes,
            ValorFormatado
        FROM ComTexto
        WHERE ValorFormatado IS NOT NULL
    ) AS src
    PIVOT (
        MAX(ValorFormatado)
        FOR Mes IN ([jan], [fev], [mar], [abr], [mai], [jun],
                    [jul], [ago], [set], [out], [nov], [dez])
    ) AS p
),

-- Junta os valores formatados com os numéricos para calcular o total anual
ComTotalLinha AS (
    SELECT 
        f.Grupo,
        f.[jan], f.[fev], f.[mar], f.[abr], f.[mai], f.[jun],
        f.[jul], f.[ago], f.[set], f.[out], f.[nov], f.[dez],
        FORMAT(
            ISNULL(n.[jan], 0) + ISNULL(n.[fev], 0) + ISNULL(n.[mar], 0) + ISNULL(n.[abr], 0) +
            ISNULL(n.[mai], 0) + ISNULL(n.[jun], 0) + ISNULL(n.[jul], 0) + ISNULL(n.[ago], 0) +
            ISNULL(n.[set], 0) + ISNULL(n.[out], 0) + ISNULL(n.[nov], 0) + ISNULL(n.[dez], 0)
        , 'C', 'pt-br') AS Total_Anual,
        CASE f.Grupo
            WHEN 'CSO - CONTR. SOCIAL ORDINÁRIA' THEN 1
            WHEN 'CSN - CONTR. SOCIAL NACIONAL' THEN 2
            WHEN 'CONVÊNIOS COM SEBRAE NA' THEN 3
            WHEN 'CONVÊNIOS, SUBV. E AUXÍLIOS' THEN 4
            WHEN 'CONTRATO INTERNO' THEN 5
            WHEN 'EMPRESAS BENEFICIADAS' THEN 6
            WHEN 'APLICAÇÕES FINANCEIRAS' THEN 7
            WHEN 'OUTRAS RECEITAS' THEN 8
            ELSE 99
        END AS OrdemGrupo
    FROM PivotFormatado f
    JOIN PivotNumerico n ON f.Grupo = n.Grupo
)

-- Resultado final com os valores por mês, total anual e total geral
SELECT 
    Grupo, [jan], [fev], [mar], [abr], [mai], [jun],
    [jul], [ago], [set], [out], [nov], [dez], Total_Anual
FROM (
    -- Linhas individuais por grupo
    SELECT 
        Grupo, [jan], [fev], [mar], [abr], [mai], [jun],
        [jul], [ago], [set], [out], [nov], [dez], Total_Anual, OrdemGrupo
    FROM ComTotalLinha

    UNION ALL

    -- Linha de total geral somando todos os grupos
    SELECT 
        'TOTAL GERAL',
        FORMAT(SUM(n.[jan]), 'C', 'pt-br'),
        FORMAT(SUM(n.[fev]), 'C', 'pt-br'),
        FORMAT(SUM(n.[mar]), 'C', 'pt-br'),
        FORMAT(SUM(n.[abr]), 'C', 'pt-br'),
        FORMAT(SUM(n.[mai]), 'C', 'pt-br'),
        FORMAT(SUM(n.[jun]), 'C', 'pt-br'),
        FORMAT(SUM(n.[jul]), 'C', 'pt-br'),
        FORMAT(SUM(n.[ago]), 'C', 'pt-br'),
        FORMAT(SUM(n.[set]), 'C', 'pt-br'),
        FORMAT(SUM(n.[out]), 'C', 'pt-br'),
        FORMAT(SUM(n.[nov]), 'C', 'pt-br'),
        FORMAT(SUM(n.[dez]), 'C', 'pt-br'),
        FORMAT(SUM(
            ISNULL(n.[jan], 0) + ISNULL(n.[fev], 0) + ISNULL(n.[mar], 0) + ISNULL(n.[abr], 0) +
            ISNULL(n.[mai], 0) + ISNULL(n.[jun], 0) + ISNULL(n.[jul], 0) + ISNULL(n.[ago], 0) +
            ISNULL(n.[set], 0) + ISNULL(n.[out], 0) + ISNULL(n.[nov], 0) + ISNULL(n.[dez], 0)
        ), 'C', 'pt-br'),
        99
    FROM PivotNumerico n
) AS Final
ORDER BY OrdemGrupo;

    """
    ),

    # Segunda consulta: Seleciona dados de despesa para o ano de 2025
    "DESPESAS":Query(
        titulo="Despesas para o ano de 2025",
        sql= 
    
    """ 
        WITH CTE_Base AS (
    SELECT 
        CONTA_FECHAMENTO,
        DATENAME(MONTH, DATA) AS MES,
        UNIFICAVALOR,
        CASE CONTA_FECHAMENTO
            WHEN 'Fundo Mútuo Inv. Empresas Emerg.' THEN 1
            WHEN 'Programa de Crédito Orientado' THEN 2
            WHEN 'Investimentos - Bens Imóveis' THEN 3
            WHEN 'Imobilizado' THEN 4
            WHEN 'Provisão p/ IRRF Rend. Fundos' THEN 5
            WHEN 'Depósitos Judiciais' THEN 6
            WHEN 'PESSOAL, ENC. E BEN.SOCIAIS' THEN 7
            WHEN 'Serviços Profissionais e Contratados' THEN 8
            WHEN 'CUSTO/DESP.OPERACIONALIZAÇÃO' THEN 9
            WHEN 'Encargos Diversos' THEN 10
            WHEN 'Liberações de Convênios' THEN 11
            WHEN 'Transferências' THEN 12
            ELSE 98
        END AS OrdemConta
    FROM FatoFechamento
    WHERE YEAR(DATA) = 2025 AND TIPO = 'DESPESA'
),
CTE_Traduzida AS (
    SELECT 
        CONTA_FECHAMENTO,
        OrdemConta,
        UNIFICAVALOR,
        CASE LOWER(MES)
            WHEN 'january' THEN 'jan'
            WHEN 'february' THEN 'fev'
            WHEN 'march' THEN 'mar'
            WHEN 'april' THEN 'abr'
            WHEN 'may' THEN 'mai'
            WHEN 'june' THEN 'jun'
            WHEN 'july' THEN 'jul'
            WHEN 'august' THEN 'ago'
            WHEN 'september' THEN 'set'
            WHEN 'october' THEN 'out'
            WHEN 'november' THEN 'nov'
            WHEN 'december' THEN 'dez'
        END AS MES_PT
    FROM CTE_Base
),
CTE_Pivotada AS (
    SELECT *
    FROM (
        SELECT 
            CONTA_FECHAMENTO,
            MES_PT,
            UNIFICAVALOR,
            OrdemConta
        FROM CTE_Traduzida
    ) AS Fonte
    PIVOT (
        SUM(UNIFICAVALOR)
        FOR MES_PT IN ([jan], [fev], [mar], [abr], [mai], [jun],
                       [jul], [ago], [set], [out], [nov], [dez])
    ) AS TabelaPivoteada
),
CTE_ComTotal AS (
    SELECT 
        UPPER(CONTA_FECHAMENTO) AS Grupo,
        [jan], [fev], [mar], [abr], [mai], [jun],
        [jul], [ago], [set], [out], [nov], [dez],
        ISNULL([jan],0) + ISNULL([fev],0) + ISNULL([mar],0) + ISNULL([abr],0) +
        ISNULL([mai],0) + ISNULL([jun],0) + ISNULL([jul],0) + ISNULL([ago],0) +
        ISNULL([set],0) + ISNULL([out],0) + ISNULL([nov],0) + ISNULL([dez],0) AS Total_Anual,
        OrdemConta
    FROM CTE_Pivotada
)
SELECT 
    Grupo,
    FORMAT([jan], 'C', 'pt-br') AS [jan],
    FORMAT([fev], 'C', 'pt-br') AS [fev],
    FORMAT([mar], 'C', 'pt-br') AS [mar],
    FORMAT([abr], 'C', 'pt-br') AS [abr],
    FORMAT([mai], 'C', 'pt-br') AS [mai],
    FORMAT([jun], 'C', 'pt-br') AS [jun],
    FORMAT([jul], 'C', 'pt-br') AS [jul],
    FORMAT([ago], 'C', 'pt-br') AS [ago],
    FORMAT([set], 'C', 'pt-br') AS [set],
    FORMAT([out], 'C', 'pt-br') AS [out],
    FORMAT([nov], 'C', 'pt-br') AS [nov],
    FORMAT([dez], 'C', 'pt-br') AS [dez],
    FORMAT(Total_Anual, 'C', 'pt-br') AS Total_Anual
FROM (
    SELECT 
        Grupo, [jan], [fev], [mar], [abr], [mai], [jun],
        [jul], [ago], [set], [out], [nov], [dez], Total_Anual, OrdemConta
    FROM CTE_ComTotal

    UNION ALL

    SELECT 
        'TOTAL GERAL',
        SUM([jan]), SUM([fev]), SUM([mar]), SUM([abr]), SUM([mai]), SUM([jun]),
        SUM([jul]), SUM([ago]), SUM([set]), SUM([out]), SUM([nov]), SUM([dez]),
        SUM(Total_Anual),
        99
    FROM CTE_ComTotal
) AS Final
ORDER BY OrdemConta;

    """
    )    
}