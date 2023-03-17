# Bibliotecas
import time
import re
import requests
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import lxml

# Aviso de Progresso
time.sleep(2)
print("Bibliotecas carregadas.")
time.sleep(2)

##########################################################################################################################

# Função de scraping dos dados da tabela no site
def filtrar_dados(soup):
    # Filtrando os autores de cada linha
    tds = soup.find_all('td')
    autores = []
    for i in range(2, len(tds), 10):
        autores_texto = tds[i].text.strip()
        autores.append(autores_texto)

    # Filtrando o LINK do chat
    inicio_url = 'https://s17.chatguru.app/'
    links_id = []
    tds = soup.find_all('td')
    for i in range(3, len(tds), 10):
        td = tds[i]
        try:
            class_list = td.find('a').get('href')
        except AttributeError:
            class_list = None
        links_id.append(class_list)
    links_id = [inicio_url + link for link in links_id]

    # Filtrando o nome do chat/pessoa
    tds = soup.find_all('td')
    pessoa_chat = []
    for i in range(3, len(tds), 10):
        pessoa_chat_texto = tds[i].text.strip()
        pessoa_chat.append(pessoa_chat_texto)

    # Filtrando o tipo
    tds = soup.find_all('td')
    tipo = []
    for i in range(4, len(tds), 10):
        td = tds[i]
        i_tag = td.find('i')
        if i_tag:
            class_list = i_tag.get('class')
            class_value = " ".join(class_list)
            tipo.append(class_value)
        else:
            tipo.append(None)

    # Filtrando a preview
    tds = soup.find_all('td')
    preview = []
    for i in range(5, len(tds), 10):
        preview_texto = tds[i].text.strip()
        if preview_texto:
            preview.append(preview_texto)
        else:
            preview.append(None)

    # Filtrando o status
    tds = soup.find_all('td')
    status = []
    for i in range(6, len(tds), 10):
        status_texto = tds[i].text.strip()
        status.append(status_texto)

    # Filtrando a data de cadastro
    tds = soup.find_all('td')
    data_cadastro = []
    for i in range(7, len(tds), 10):
        data_cadastro_texto = tds[i].text.strip()
        data_cadastro.append(data_cadastro_texto)

    # Filtrando a data de envio
    tds = soup.find_all('td')
    data_envio = []
    for i in range(8, len(tds), 10):
        data_envio_texto = tds[i].text.strip()
        data_envio.append(data_envio_texto)
        
    # Obtendo o valor de is_out
    direcao = soup.find('select', {'name': 'is_out'}).find('option', {'value': 'True'}).text

    # Criando um DataFrame com os dados filtrados
    df = pd.DataFrame({
        'Autor': autores,
        'Link': links_id,
        'Nome Pessoa': pessoa_chat,
        'Tipo': tipo,
        'Preview': preview,
        'Status': status,
        'Data Cadastro': data_cadastro,
        'Data Envio': data_envio
    })

    # Criando a coluna "Direção"
    df['Direção'] = [direcao_escolhida] * len(df.index)

    return df

# Função de descobrir a última página
def obter_numero_penultima_pagina(driver):
    # Encontrar o elemento da penúltima página
    paginacao = driver.find_element_by_css_selector('ul.pagination')
    paginas = paginacao.find_elements_by_tag_name('li')
    penultima_pagina = paginas[-2]

    # Extrair o número da penúltima página
    numero_penultima_pagina = penultima_pagina.find_element_by_tag_name('a').get_attribute('data-page')
    return int(numero_penultima_pagina)

# Mensagem de progresso
print("Funções carregadas com sucesso.")
time.sleep(2)

##########################################################################################################################

# Marcando o início
print("Iniciando a extração de dados do ChatGURU.")
time.sleep(5)

# Inicialize o webdriver do navegador de sua escolha
driver = webdriver.Chrome(ChromeDriverManager().install())

# Acesse o site
driver.get("https://s17.chatguru.app/")

# Encontre o campo de e-mail e preencha com seu endereço de e-mail
email = driver.find_element_by_id("email")
email.send_keys("backoffice@grupovoz.com.br")

# Encontre o campo de senha e preencha com sua senha
senha = driver.find_element_by_id("password")
senha.send_keys("Bac@guru#3250")

# Encontre o botão de login e clique nele
botao_login = driver.find_element_by_xpath("//button[@type='submit']")
botao_login.click()

# Aguarde a página carregar após o login
driver.implicitly_wait(10)

# Mensagem de progresso
print("Login efetuado com sucesso.")
time.sleep(2)

# Navegar para a página
driver.get('https://s17.chatguru.app/reports/messages')
time.sleep(3)
print("Página de Relatório de Mensagens carregada com sucesso.")
time.sleep(3)

##########################################################################################################################

### Essa parte precisará de algum nível de interação ###
print("Nessa parte, você precisará selecionar o período de tempo para fazer a extração de dados")
time.sleep(2)

# Selecionar a opção "Recebida"
select_element = Select(driver.find_element_by_id('is_out'))
select_element.select_by_value('False')
direcao_escolhida = select_element.first_selected_option.text

## Selecionar data inicial
time.sleep(2)
print("ATENÇÃO: JANELA DE TEMPO NÃO PODE SER SUPERIOR À 90 DIAS DE ACORDO COM O SITE!!!")
time.sleep(4)
print("Ou seja, intervalo de tempo de no máximo 3 meses por consulta")
time.sleep(4)
data_criacao = driver.find_element_by_id("created_from")
# Limpa o campo input
data_criacao.clear()
# Solicita que o usuário insira uma data
nova_data = input("Insira uma nova data final (formato YYYY-MM-DD): ")
# Insere a nova data no campo input
data_criacao.send_keys(nova_data)
# Atualiza a propriedade value do campo com a nova data
driver.execute_script("arguments[0].value = arguments[1]", data_criacao, nova_data)

## Selecionar data final
data_final = driver.find_element_by_id("created_to")
# Limpa o campo input
data_final.clear()
# Solicita que o usuário insira uma data
nova_data_final = input("Insira uma nova data final (formato YYYY-MM-DD): ")
# Insere a nova data no campo input
data_final.send_keys(nova_data_final)
# Atualiza a propriedade value do campo com a nova data
driver.execute_script("arguments[0].value = arguments[1]", data_final, nova_data_final)
print("Por favor, aguarde.")

# Tempo de espera para evitar bugar a página
time.sleep(5)

# Apertar o botão "Ver Relatório"
ver_relatorio_btn = driver.find_element_by_class_name('messages_reports_submit')
ver_relatorio_btn.click()
time.sleep(5)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
#soup

# Esperar um tempo para não bugar a página
time.sleep(5)

# Aviso de Progresso
print("Tudo pronto, por favor aguarde.")
time.sleep(2)

##########################################################################################################################

# Indo para a parte 1
print("Iniciando parte 1, fazendo a extração das mensagens Recebidas")

# só para não ter que recarregar tudo de novo
soup = BeautifulSoup(html, 'html.parser')

# Inicializa um DataFrame vazio
df_total_parte_1 = pd.DataFrame()

# Saber última página do site, que será usada para o contador do loop
ultima_pagina = obter_numero_penultima_pagina(driver)
print("O loop precisa ir até a página: " + str(ultima_pagina))
time.sleep(5)

# Inicia o scraping da página 1
df_pagina1 = filtrar_dados(soup)
print("O DF da página #1 está concluído.")
time.sleep(3)

# Adiciona os dados da página 1 ao DataFrame total
df_total_parte_1 = pd.concat([df_total_parte_1, df_pagina1])
print("O DF da página #1 está no DF geral.")
time.sleep(3)

# Iniciar o loop, para pegar os dados das páginas de 1 a 4
num_pagina = 1

# Tempo de espera, para evitar possíveis bugs no armazenamento do DataFrame da página 1
time.sleep(7)

# Variável de tentativas
tentativas = 0
tentativas_apos_botao = 0

# Início do Loop, até a última página      
while num_pagina <= ultima_pagina:
    try:
        # Encontrar e apertar o botão de 'próxima página'
        botao = driver.find_element_by_css_selector("i.fa.fa-chevron-right")
        botao.click()
        # Aguardar para evitar bug
        time.sleep(3)
        num_pagina += 1
        print("Página atual: " + str(num_pagina))
        if num_pagina > ultima_pagina:
            break
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        print("Registrado nova entrada para a variável soup, página :" + str(num_pagina))
        time.sleep(2)
    except NoSuchElementException:
        print("Botão não encontrado. Tentando novamente em 3 segundos...")
        time.sleep(3)
        tentativas += 1 # Aumentar a contagem de tentativas
        print("Total de tentativas: " + str(tentativas))
        time.sleep(3)
        if num_pagina >= ultima_pagina:
            break
    except:
        print("Erro ao clicar no botão. Tentando novamente em 3 segundos...")
        time.sleep(10)
        tentativas += 1 # Aumentar a contagem de tentativas
        print("Total de tentativas: " + str(tentativas))
        time.sleep(5)
        if num_pagina >= ultima_pagina:
            break
        
    try:
        # Extrair os dados da página atual e adicionar ao DataFrame total
        df_proxima_pagina = filtrar_dados(soup)
        df_total_parte_1 = pd.concat([df_total_parte_1, df_proxima_pagina])
        time.sleep(3)
        print("Tudo ok, indo para a próxima página.") 
    except NoSuchElementException:
        print("Elemento no scraping não encontrado. Tentando novamente em 3 segundos...")
        time.sleep(3)
        tentativas_apos_botao += 1 # Aumentar a contagem de tentativas
        print("Total de tentativas: " + str(tentativas_apos_botao))
        time.sleep(3)
    except:
        print("Erro no scraping. Tentando novamente em 3 segundos...")
        time.sleep(3)

print("Chegamos no final do loop")
# Criação e organização do DataFrame final
df_total_parte_1 = df_total_parte_1.reset_index(drop=True)
df_total_parte_1 = df_total_parte_1.iloc[::-1].reset_index(drop=True)
time.sleep(2)
time.sleep(2)

##########################################################################################################################

# Indo para a parte 2
print("Iniciando parte 2, fazendo a extração das mensagens Enviadas")
time.sleep(2)

##########################################################################################################################

# Selecionar a opção "Recebida"
select_element = Select(driver.find_element_by_id('is_out'))
select_element.select_by_value('True')
direcao_escolhida = select_element.first_selected_option.text

## Selecionar data inicial
data_criacao = driver.find_element_by_id("created_from")
# Limpa o campo input
data_criacao.clear()
# Solicita que o usuário insira uma data
nova_data = nova_data
# Insere a nova data no campo input
data_criacao.send_keys(nova_data)
# Atualiza a propriedade value do campo com a nova data
driver.execute_script("arguments[0].value = arguments[1]", data_criacao, nova_data)

## Selecionar data final
data_final = driver.find_element_by_id("created_to")
# Limpa o campo input
data_final.clear()
# Solicita que o usuário insira uma data
nova_data_final = nova_data_final
# Insere a nova data no campo input
data_final.send_keys(nova_data_final)
# Atualiza a propriedade value do campo com a nova data
driver.execute_script("arguments[0].value = arguments[1]", data_final, nova_data_final)
print("Por favor, aguarde.")

# Tempo de espera para evitar bugar a página
time.sleep(5)

# Apertar o botão "Ver Relatório"
ver_relatorio_btn = driver.find_element_by_class_name('messages_reports_submit')
ver_relatorio_btn.click()
time.sleep(5)
html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
#soup

# Esperar um tempo para não bugar a página
time.sleep(5)

# Aviso de Progresso
print("Tudo pronto, por favor aguarde.")
time.sleep(2)

##########################################################################################################################

# Indo para a parte 2
print("Iniciando parte 2, fazendo a extração das mensagens Enviadas")

# só para não ter que recarregar tudo de novo
soup = BeautifulSoup(html, 'html.parser')

# Inicializa um DataFrame vazio
df_total_parte_2 = pd.DataFrame()

# Saber última página do site, que será usada para o contador do loop
ultima_pagina = obter_numero_penultima_pagina(driver)
print("O loop precisa ir até a página: " + str(ultima_pagina))
time.sleep(5)

# Inicia o scraping da página 1
df_pagina1 = filtrar_dados(soup)
print("O DF da página #1 está concluído.")
time.sleep(3)

# Adiciona os dados da página 1 ao DataFrame total
df_total_parte_2 = pd.concat([df_total_parte_2, df_pagina1])
print("O DF da página #1 está no DF geral.")
time.sleep(3)

# Iniciar o loop, para pegar os dados das páginas de 1 a 4
num_pagina = 1

# Tempo de espera, para evitar possíveis bugs no armazenamento do DataFrame da página 1
time.sleep(7)

# Variável de tentativas
#tentativas = 0
#tentativas_apos_botao = 0

# Início do Loop, até a última página      
while num_pagina <= ultima_pagina:
    try:
        # Encontrar e apertar o botão de 'próxima página'
        botao = driver.find_element_by_css_selector("i.fa.fa-chevron-right")
        botao.click()
        # Aguardar para evitar bug
        time.sleep(3)
        num_pagina += 1
        print("Página atual: " + str(num_pagina))
        if num_pagina > ultima_pagina:
            break
        time.sleep(2)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        print("Registrado nova entrada para a variável soup, página :" + str(num_pagina))
        time.sleep(2)
    except NoSuchElementException:
        print("Botão não encontrado. Tentando novamente em 3 segundos...")
        time.sleep(3)
        tentativas += 1 # Aumentar a contagem de tentativas
        print("Total de tentativas: " + str(tentativas))
        time.sleep(3)
        if num_pagina >= ultima_pagina:
            break
    except:
        print("Erro ao clicar no botão. Tentando novamente em 3 segundos...")
        time.sleep(10)
        tentativas += 1 # Aumentar a contagem de tentativas
        print("Total de tentativas: " + str(tentativas))
        time.sleep(5)
        if num_pagina >= ultima_pagina:
            break
        
    try:
        # Extrair os dados da página atual e adicionar ao DataFrame total
        df_proxima_pagina = filtrar_dados(soup)
        df_total_parte_2 = pd.concat([df_total_parte_2, df_proxima_pagina])
        time.sleep(3)
        print("Tudo ok, indo para a próxima página.")
    except NoSuchElementException:
        print("Elemento no scraping não encontrado. Tentando novamente em 3 segundos...")
        time.sleep(3)
        tentativas_apos_botao += 1 # Aumentar a contagem de tentativas
        print("Total de tentativas: " + str(tentativas_apos_botao))
        time.sleep(3)
    except:
        print("Erro no scraping. Tentando novamente em 3 segundos...")
        time.sleep(3)

print("Chegamos no final do loop")
# Criação e organização do DataFrame final
df_total_parte_2 = df_total_parte_2.reset_index(drop=True)
df_total_parte_2 = df_total_parte_2.iloc[::-1].reset_index(drop=True)
time.sleep(2)

##########################################################################################################################

# Concatenação dos dataframes de direção 'Enviada e 'Recebida'
df_total = pd.concat([df_total_parte_1, df_total_parte_2])

# Organização dos IDs por Index
df_total = df_total.reset_index(drop=True)
df_total = df_total.iloc[::-1].reset_index(drop=True)
df_total.reset_index(drop=True, inplace=True)
df_total.rename(columns={'index': 'ID'}, inplace=True)
df_total.insert(0, 'ID', range(1, 1 + len(df_total)))

## Criação de arquivo em CSV para download e posterior anexo ao banco de dados
# Solicita que o usuário insira o nome do arquivo
time.sleep(3)
nome_arquivo = input("Insira o nome do arquivo CSV: (por exemplo, CHATGURU_JAN_23")
# Salva o arquivo CSV com o nome inserido pelo usuário
df_total.to_csv(nome_arquivo + ".csv", index=False)

##########################################################################################################################

# Finalizando a aplicação
time.sleep(2)
print("O arquivo " + nome_arquivo + ".csv " + "foi gerado, favor conferir o download.")
time.sleep(3)
print("A aplicação será finalizada em aproximadamente 5 segundos.")
time.sleep(8)
driver.close()