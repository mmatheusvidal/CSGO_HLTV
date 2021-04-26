from selenium.webdriver import Chrome
from time import sleep
import json
import pandas as pd

browser = Chrome()
first_page = 'https://www.hltv.org/results'
other_pages = 'https://www.hltv.org/results?offset=' #100; 200; 300; 400...
resultado = []
browser.get('https://www.hltv.org/')
sleep(2)

def read_result_raw_list(pagina, resultado):
    browser.get(pagina)
    sleep(2)
    jogos = browser.find_elements_by_class_name('a-reset')
    for jogo in range(len(jogos)):
        dict_jogo = {"jogo": jogos[jogo].text,
                "link": jogos[jogo].get_attribute('href')}
        resultado.append(dict_jogo)
    return resultado

def results(paginas_link, resultado):
    for i in paginas_link:
        read_result_raw_list(i, resultado)
    return resultado

def mount_other_pages(list_paginas):
    other_pages = 'https://www.hltv.org/results?offset='
    paginas_link = []
    for i in list_paginas:
        pag = other_pages + str(i)
        paginas_link.append(pag)
    return paginas_link

def list_paginas(pagina):
    browser.get(pagina)
    sleep(2)
    paginas = browser.find_element_by_class_name('pagination-data').text[11:]
    qtd = round(int(paginas)/100)
    a = 0
    list_paginas = [0]
    for i in range(0,qtd):
        a = a + 100
        list_paginas.append(a)
    return list_paginas

def write_file(resultado):
    f=open('teste_resultados.json','w')
    f.write('[')
    for i in range(len(resultado)):
        json.dump(resultado[i], f)
        f.write(',\n')
    f.write(']')
    f.close()

#Execução
#list_paginas = list_paginas(first_page)
#paginas_link = mount_other_pages(list_paginas)
#resultado = results(paginas_link, resultado)
#write_file(resultado)
