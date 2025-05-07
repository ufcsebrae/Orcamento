# Sistema de Gestão de Orçamento

Este projeto é um sistema para gestão de orçamento que realiza consultas em um banco de dados SQL Server, processa os dados de receitas e despesas, calcula o superávit/déficit, e envia relatórios por e-mail utilizando o Microsoft Outlook.

---

## Módulos e Funcionalidades

### 1. `main.py`
Arquivo principal que:
- Realiza consultas SQL para obter receitas e despesas.
- Processa os dados para calcular o superávit/déficit.
- Gera um DataFrame com os resultados.
- Envia relatórios por e-mail.

#### Principais Funções:
- **`connect_to_sql_server`**: Conecta ao banco de dados e executa as queries.
- **`print_table`**: Exibe os resultados formatados no console.
- **`enviar_relatorio_email`**: Envia o relatório por e-mail.

---

### 2. `connection/engine.py`
Gerencia a conexão com o banco de dados e manipulação de tabelas.

#### Principais Funções:
- **`connect_to_sql_server(queries)`**:
  - Conecta ao SQL Server e executa a query passada como parâmetro.
  - Retorna os resultados como um DataFrame.
- **`print_table(df, title)`**:
  - Exibe um DataFrame formatado no console usando o pacote `rich`.
- **`limpar_e_converter(df)`**:
  - Limpa e converte valores monetários (ex.: `R$ 17.532,15`) para numérico.

---

### 3. `connection/query.py`
Contém as queries SQL para buscar receitas e despesas no banco de dados.

#### Estrutura:
- **`queries["RECEITAS"]`**: Query para buscar receitas.
- **`queries["DESPESAS"]`**: Query para buscar despesas.

---

### 4. `email_utils/email_sender.py`
Gerencia o envio de relatórios por e-mail.

#### Principais Funções:
- **`formatar_moeda(valor)`**:
  - Formata valores numéricos para o formato monetário brasileiro (`R$ 1.000,00`).
- **`enviar_relatorio_email(destinatario, assunto, dataframeTOTAL, dataframeCC, dataframeID)`**:
  - Envia um e-mail com os DataFrames formatados como tabelas HTML.
  - Utiliza o Microsoft Outlook para envio.
  - **`destinatario`**: "orcamento@sp.sebrae.com.br;marcelocp@sebraesp.com.br"

---

### 5. `templates/email_template.html`
Template HTML para o corpo do e-mail. Contém placeholders para:
- Assunto.
- Tabelas de receitas, despesas e superávit/déficit.
- Texto personalizado.

---

## Instalação e Configuração

### 1. Pré-requisitos
- Python 3.8 ou superior.
- Microsoft Outlook instalado e configurado.
- Acesso ao banco de dados SQL Server.

### 2. Instale as Dependências
Crie um ambiente virtual e instale as dependências:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r [requirements.txt](http://_vscodecontentref_/4)
```

### 3. Configuração do Banco de Dados
Certifique-se de que as queries em connection/query.py estão configuradas corretamente para o seu banco de dados.
### 4. Configuração do E-mail
Certifique-se de que o Microsoft Outlook está configurado no computador onde o script será executado.
Atualize os destinatários no arquivo main.py:
```bash
destinatario = "orcamento@sp.sebrae.com.br;marcelocp@sebraesp.com.br"
```
# Como Executar
    1.Navegue até o diretório do projeto:
```bash
    cd "c:\Users\cesargl\OneDrive - SERVICO DE APOIO AS MICRO E PEQUENAS EMPRESAS DE SAO PAULO - SEBRAE\Área de Trabalho\Orcamento"
``` 
    2.Execute o script principal:
```bash
    python main.py
```
# Atualização do Projeto
    1.Adicionar Novas Queries
     - Adicione novas queries no arquivo connection/query.py no formato:
```bash
    queries["NOME_DA_QUERY"] = Query(
    titulo="Título da Query",
    sql="SELECT * FROM tabela WHERE ..."
)
```
    2. Atualizar o Template de E-mail
     - Edite o arquivo templates/email_template.html para personalizar o corpo do e-mail.

    3. Adicionar Novas Funcionalidades
     - Crie novos módulos ou funções conforme necessário.
     - Certifique-se de atualizar os imports no main.py.

# Contribuição
    1. Faça um fork do repositório.
    2. Crie uma branch para sua feature:
```bash
git checkout -b minha-feature
```
    3. Faça commit das suas alterações:
```bash
git commit -m "Adiciona nova funcionalidade"
```
    4. Envie para o repositório remoto:
```bash
git push origin minha-feature
```
    5. Abra um Pull Request.
    
# Licença
Este projeto é privado e de uso exclusivo do SEBRAE-SP.

Se precisar de mais informações, entre em contato com o administrador do projeto. ```





