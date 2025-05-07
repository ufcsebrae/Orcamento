from sqlalchemy import engine_from_config, text
import pandas as pd
from rich.console import Console
from rich.table import Table
from rich.text import Text  # Importar para formatar células
from rich import box
import pandas as pd

def connect_to_sql_server(queries):    
    """Conecta ao SQL Server, executa uma consulta e imprime o resultado com formatação condicional."""

    # Configuração do servidor SQL Server
    servername = "spsvsql39\\metas"  # Nome do servidor SQL
    dbname = "FINANCA"  # Nome do banco de dados
    driver = "ODBC+Driver+17+for+SQL+Server"  # Driver ODBC para conexão

    # Configuração da URL de conexão para o SQLAlchemy
    config = {
        'sqlalchemy.url': f'mssql+pyodbc://@{servername}/{dbname}?trusted_connection=yes&driver={driver}'
    }

    # Criação do engine de conexão com base na configuração
    engine = engine_from_config(config, prefix='sqlalchemy.')

    # Estabelece a conexão com o banco de dados
    with engine.connect() as connection:
        # Executa a consulta SQL passada como parâmetro
        result = connection.execute(text(queries.sql))
        
        # Converte o resultado da consulta em um DataFrame
        df = pd.DataFrame(result.fetchall(), columns=result.keys())

        # Configuração do console para exibir a tabela formatada
        console = Console()
        table = Table(show_header=True, header_style="bold magenta", box=box.SQUARE)
        table.title = queries.titulo  # Título da tabela
        table.title_justify = "left"  # Alinhamento do título
        table.title_style = "bold blue"  # Estilo do título
        table.border_style = "bold blue"  # Estilo da borda
        table.row_styles = ["none", "dim"]  # Estilos alternados para as linhas
        table.show_lines = True  # Exibe linhas entre as linhas da tabela

        # Adiciona as colunas ao objeto Table
        for col in df.columns:
            table.add_column(str(col))

        # Adiciona as linhas ao objeto Table com formatação condicional
        for row in df.itertuples(index=False):
            formatted_row = []  
            for cell in row:
                if isinstance(cell, (int, float)):
                    # Formata números: verde para positivo, vermelho para negativo
                    if cell < 0:
                        text_cell = Text(str(cell), style="bold red")
                    else:
                        text_cell = Text(str(cell), style="bold green")
                else:
                    # Formata texto normal
                    text_cell = Text(str(cell) if cell is not None else "")
                formatted_row.append(text_cell)

            # Adiciona a linha formatada à tabela
            table.add_row(*formatted_row)

        # Exibe a tabela formatada no console
        console.print(table)
         # Retorna o resultado da consulta como um DataFrame
        return df
def print_table(df, title):
    """Exibe um DataFrame formatado como tabela no console."""
    console = Console()
    table = Table(show_header=True, header_style="bold magenta", box=box.SQUARE)
    table.title = title  # Título da tabela
    table.title_justify = "left"  # Alinhamento do título
    table.title_style = "bold blue"  # Estilo do título
    table.border_style = "bold blue"  # Estilo da borda
    table.row_styles = ["none", "dim"]  # Estilos alternados para as linhas
    table.show_lines = True  # Exibe linhas entre as linhas da tabela

    # Adiciona as colunas ao objeto Table
    for col in df.columns:
        table.add_column(str(col))

    # Adiciona as linhas ao objeto Table com formatação condicional
    for row in df.itertuples(index=False):
        formatted_row = []
        for cell in row:
            if isinstance(cell, (int, float)):
                # Formata números como moeda: verde para positivo, vermelho para negativo
                if cell < 0:
                    text_cell = Text(f"R$ {cell:,.2f}", style="bold red")
                else:
                    text_cell = Text(f"R$ {cell:,.2f}", style="bold green")
            else:
                # Formata texto normal
                text_cell = Text(str(cell) if cell is not None else "")
            formatted_row.append(text_cell)

        # Adiciona a linha formatada à tabela
        table.add_row(*formatted_row)

    # Exibe a tabela formatada no console
    console.print(table)

# Função para limpar e converter os valores para numérico
def limpar_e_converter(df):
    df.iloc[:, 1:-1] = (
        df.iloc[:, 1:-1]
        .replace(r'\(.*?\)', '', regex=True)  # Remove texto entre parênteses, como "(P)"
        .replace(r'[R$\s]', '', regex=True)  # Remove "R$", espaços e outros caracteres
        .replace(r'\.', '', regex=True)     # Remove separadores de milhares
        .replace(r',', '.', regex=True)     # Substitui vírgulas por pontos
        .apply(pd.to_numeric, errors='coerce')  # Converte para numérico
    )
    return df