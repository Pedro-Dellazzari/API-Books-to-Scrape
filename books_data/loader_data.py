#importando bibliotecas
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urljoin

import duckdb

from handsome_log import get_logger

logger = get_logger(__name__)


#banco 
con = duckdb.connect(database='books.db', read_only=False)

con.execute("""
CREATE TABLE IF NOT EXISTS livros(
    upc_livro TEXT PRIMARY KEY,
    titulo TEXT,
    imagem TEXT,
    categoria TEXT,
    valor_principal_em_euros DOUBLE,
    valor_principal_em_reais DOUBLE,
    inventario INTEGER,
    review TEXT,
    sinopse TEXT,    
    num_reviews INTEGER,
    link TEXT
    )
""")


### FUNÇÕES 
url_principal = 'https://books.toscrape.com/'
url_de_paginas = 'https://books.toscrape.com/catalogue/page-{}.html'

livros_links = []

valor_euro_para_real = 6.35

def coleta_de_links(url):
    page = 1
    while True:
        resposta = requests.get(url)

        if resposta.status_code == 200:
            logger.success(f'Requisição bem-sucedida para {url}')
        else:
            logger.critical(f'Falha na requisição para {url}')
            return None
        
        soup = BeautifulSoup(resposta.text, 'html.parser')

        #achando o ol com os li dos livros
        books = soup.find_all('article', class_='product_pod')

        for book in books:
            link = book.find('a')['href']
            livros_links.append(link)

        #verificando se existe paginação
        if verificar_paginacao(soup):
            #se existir, pega o link da proxima pagina
            page += 1
            url = url_de_paginas.format(page)

            logger.success(f'Próxima página: {url}')
            continue  # Volta para o início do loop para processar a próxima página
            #break
        else:
            logger.success('Não há mais páginas para processar.')
            break

def coleta_atributos_livro(link):
    resposta = requests.get(link)

    soup = BeautifulSoup(resposta.text, 'html.parser')

    # Extraindo atributos do livro
    titulo = soup.find('h1').text
    imagem = 'https://books.toscrape.com/' + soup.find('img')['src'].replace('../', '')
    categoria = soup.find('ul', class_='breadcrumb').find_all('li')[2].text.strip()

    preco_eur = float(re.search(r'\d+\.\d+', soup.find('p', class_='price_color').text).group())
    preco_brl = preco_eur * valor_euro_para_real

    estoque = int(re.search(r'\d+', soup.find('p', class_='instock availability').text.strip()).group())
    review = soup.find('p', class_='star-rating')['class'][1]
    sinopse = soup.find('meta', attrs={'name': 'description'})['content'].strip()
    sinopse = sinopse.encode('latin1').decode('utf-8')
    upc = soup.find('th', text='UPC').find_next_sibling('td').text
    num_reviews = int(soup.find('th', text='Number of reviews').find_next_sibling('td').text)

    con.execute("""
        INSERT OR REPLACE INTO livros VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (upc, titulo, imagem, categoria, preco_eur, preco_brl, estoque, review, sinopse, num_reviews, link))
#Função de paginação
def verificar_paginacao(soup):
    #vendo se existe o botão "next"
    proxima_pagina = soup.find('li', class_='next')
    if proxima_pagina:
        logger.success('Próxima página encontrada.')
        return True
    else:
        logger.warning('Próxima página não encontrada.')
        return False

if __name__ == "__main__":
    logger.startup('Inicando carregando de dados dos livros')
    dados = coleta_de_links(url_principal)

    #livros_links = livros_links[:10]  #  !Limitando a 10 links para teste

    for link in livros_links:
        # Corrigindo o link: se não tiver 'catalogue', adiciona
        if 'catalogue/' not in link:
            link = 'catalogue/' + link.lstrip('./')

        # Corrige qualquer ../ e monta URL completa corretamente
        link_completo = urljoin(url_principal, link)

        logger.info(f'Coletando atributos do livro: {link_completo}')
        
        try:
            coleta_atributos_livro(link_completo)
        except Exception as e:
            logger.error(f"Não foi possível pegar a info do livro: {e}")
            pass

    con.close()
