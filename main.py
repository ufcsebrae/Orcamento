from connection.engine import connect_to_sql_server, print_table, limpar_e_converter  # Importa funções para conectar ao SQL Server e exibir tabelas
from connection.query import queries  # Importa o dicionário de consultas SQL pré-definidas
from email_sender import enviar_relatorio_email  # Importa função para enviar e-mail com o relatório
import pandas as pd
from datetime import datetime


# Executa as consultas e armazena os DataFrames retornados
df_despesas = connect_to_sql_server(queries["DESPESAS"])
df_receitas = connect_to_sql_server(queries["RECEITAS"])

# Filtra a linha "TOTAL GERAL" de ambos os DataFrames e cria cópias explícitas
total_despesas = df_despesas[df_despesas['Grupo'] == 'TOTAL GERAL'].copy()
total_receitas = df_receitas[df_receitas['Grupo'] == 'TOTAL GERAL'].copy()

# Limpa e converte os valores de despesas e receitas
total_despesas = limpar_e_converter(total_despesas)
total_receitas = limpar_e_converter(total_receitas)

# Subtrai as despesas das receitas para cada mês
superavit_deficit = total_receitas.iloc[:, 1:-1].values - total_despesas.iloc[:, 1:-1].values

# Cria um novo DataFrame com o resultado
meses = df_receitas.columns[1:-1]  # Obtém os nomes das colunas de meses
df_superavit_deficit = pd.DataFrame(superavit_deficit, columns=meses)
df_superavit_deficit.insert(0, 'Grupo', ['SUPERÁVIT/DÉFICIT'])  # Adiciona a coluna "Grupo"

# Calcula o total geral (soma dos valores de todos os meses)
df_superavit_deficit['Total Geral'] = df_superavit_deficit[meses].sum(axis=1)

# Calcula o superávit sem a linha de receita "APLICAÇÕES FINANCEIRAS"
aplicacoes_financeiras = df_receitas[df_receitas['Grupo'] == 'APLICAÇÕES FINANCEIRAS'].copy()
aplicacoes_financeiras = limpar_e_converter(aplicacoes_financeiras)
total_aplicacoes = aplicacoes_financeiras.iloc[:, 1:-1].values  # Obtém os valores de "APLICAÇÕES FINANCEIRAS"

# Calcula o superávit sem o valor de "APLICAÇÕES FINANCEIRAS"
superavit_sem_aplicacoes = total_receitas.iloc[:, 1:-1].values - total_aplicacoes - total_despesas.iloc[:, 1:-1].values

# Adiciona uma nova linha ao DataFrame com o resultado
nova_linha = pd.DataFrame(
    superavit_sem_aplicacoes, 
    columns=meses
)
nova_linha.insert(0, 'Grupo', ['SUPERÁVIT/DÉFICIT (SEM APLICAÇÕES FINANCEIRAS)'])
nova_linha['Total Geral'] = nova_linha[meses].sum(axis=1)

# Adiciona a nova linha ao DataFrame de superávit/déficit
df_superavit_deficit = pd.concat([df_superavit_deficit, nova_linha], ignore_index=True)

# Exibe o DataFrame de Superávit/Déficit atualizado
print_table(df_superavit_deficit, "Superávit/Déficit por Mês")

df2 = df_despesas
df3 = df_receitas
df4 = df_superavit_deficit

destinatario = "orcamento@sp.sebrae.com.br"
assunto = f"Prévia Orçamento - {datetime.now().strftime('%d/%m/%Y')}"

enviar_relatorio_email(destinatario, assunto, df2,df3,df4)