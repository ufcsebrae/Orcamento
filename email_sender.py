import win32com.client as win32
import os
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import pandas as pd


def formatar_moeda(valor):
    """Formata valores numéricos para o formato monetário brasileiro."""
    if isinstance(valor, (int, float)):
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return valor  # Retorna como está se não for numérico


def enviar_relatorio_email(destinatario, ASSUNTO, dataframeTOTAL, dataframeCC, dataframeID):
    data_hoje = datetime.today().strftime("%d/%m/%Y")
    TEXTO_CORPO = f"""
    <p>Prezados,</p>
    <p>Segue prévia da execução das despesas e receitas atualizada no dia <strong>{data_hoje}</strong>.</p>"""

    # Limpeza dos DataFrames: substituir NaN/None por string vazia
    dataframeTOTAL = dataframeTOTAL.fillna("").infer_objects(copy=False)
    dataframeCC = dataframeCC.fillna("").infer_objects(copy=False)
    dataframeID = dataframeID.fillna("").infer_objects(copy=False)

    # Formatação de moeda apenas para o dataframeID
    dataframeID = dataframeID.map(formatar_moeda)

    # Obtendo o caminho da pasta atual para carregar o template
    caminho_atual = os.path.dirname(os.path.abspath(__file__))
    env = Environment(loader=FileSystemLoader(caminho_atual))
    
    try:
        template = env.get_template("email_template.html")
    except Exception as e:
        print(f"❌ Erro ao carregar o template: {e}")   
        return

    # Renderizando o corpo do e-mail com o template HTML
    CORPO = template.render(
        assunto=ASSUNTO,
        tabelas=dataframeTOTAL.to_html(index=False, justify="center", border=1, classes="table table-striped table-bordered"),
        tabelasCC=dataframeCC.to_html(index=False, justify="center", border=1, classes="table table-striped table-bordered"),
        tabelasID=dataframeID.to_html(index=False, justify="center", border=1, classes="table table-striped table-bordered"),
        texto_email=TEXTO_CORPO
    )

    # Enviando o e-mail via Outlook
    try:
        outlook = win32.Dispatch("Outlook.Application")
        mensagem = outlook.CreateItem(0)
        mensagem.Subject = ASSUNTO
        mensagem.HTMLBody = CORPO
        mensagem.To = destinatario

        mensagem.Send()
        print("📧 E-mail enviado com sucesso!")

    except Exception as e:
        print(f"❌ Erro ao enviar o e-mail: {e}")