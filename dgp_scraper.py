import time, os, json, threading
from playwright.sync_api import sync_playwright, TimeoutError
#import tools

load_time = 2

def create_base_file(input):
    file_path = os.path.join('DGP', f"{input}.csv")
    with open(file_path, "w", encoding="utf-8") as f:
            f.write('Grupo;Situação;Ano Formação;Líder;Instituição;Unidade;Área predominante;UF;Repercussão;Linhas de Pesquisa;Instituições Parceiras;Indicadores de RH;link\n')
    
def escreve_grupos(data, input):
    # Escreve em arquivo
    file_path = os.path.join('DGP', f"{input}.csv")
    with open(file_path, "a", encoding="utf-8") as f:
        for item in data:
            f.write(item)
            if item != data[-1]:
                f.write(';')
        f.write('\n')
    print(f"[{input}] Grupos armazenados", f"{input}.log")

def pega_dados_curriculo(pagina, input):
    data = []
    
    # Título do curriculo
    data.append(pagina.query_selector(f'div[id="tituloImpressao"]').inner_text().split('\n')[2])
    
    # Situação
    data.append(pagina.query_selector(f'div[id="identificacao"]').query_selector(f'fieldset').query_selector_all('div')[1].inner_text())
    
    # Ano Formação
    data.append(pagina.query_selector(f'div[id="identificacao"]').query_selector(f'fieldset').query_selector_all('div')[3].inner_text())
    
    # Líder
    data.append(pagina.query_selector(f'div[id="identificacao"]').query_selector(f'fieldset').query_selector_all('div')[9].inner_text().split('\n')[0])
    
    # Instituição
    data.append(pagina.query_selector(f'div[id="identificacao"]').query_selector(f'fieldset').query_selector_all('div')[13].inner_text())
    
    # Unidade
    uni = pagina.query_selector(f'div[id="identificacao"]').query_selector(f'fieldset').query_selector_all('div')
    if(len(uni) >= 16):
        data.append(uni[15].inner_text())
    else:
        data.append("")
    
    # Área predominante
    data.append(pagina.query_selector(f'div[id="identificacao"]').query_selector(f'fieldset').query_selector_all('div')[11].inner_text().replace(';', ','))
    
    # UF
    data.append(pagina.query_selector(f'div[id="endereco"]').query_selector(f'fieldset').query_selector_all('div')[9].inner_text())
    
    # Recuperar Repercussão
    rep = pagina.query_selector(f'div[id="repercussao"]')
    if(rep != None):
        data.append(rep.query_selector(f'p').inner_text().replace(';', ','))
    else:
        data.append("")
        
    # Linhas de Pesquisa
    linhas_de_pesquisa = []
    lp = pagina.query_selector(f'tbody[id="idFormVisualizarGrupoPesquisa:j_idt247_data"]')
    if(lp != None):
        lp = lp.query_selector_all('tr')
        for item in lp:
            campos = item.query_selector_all('td')
            if len(campos) == 1:
                break
            linhas_de_pesquisa.append('{"Nome":' + campos[0].inner_text().replace(';', ',') + 
                              ',"Q_Estudantes":' + campos[1].inner_text().replace(';', ',') + 
                              ',"Q_Pesquisadores":' + campos[2].inner_text().replace(';', ',') + '}')
        data.append('|'.join(linhas_de_pesquisa))
    else:
        data.append("")
        
        
    # Instituições Parceiras
    instituicoes_parceiras = []
    ip = pagina.query_selector(f'tbody[id="idFormVisualizarGrupoPesquisa:j_idt384_data"]')
    if(ip != None):
        ip = ip.query_selector_all('tr')
        for item in ip:
            campos = item.query_selector_all('td')
            if len(campos) == 1:
                break
            instituicoes_parceiras.append('{"Nome":' + campos[0].inner_text().replace(';', ',') + 
                                         ',"Sigla":' + campos[1].inner_text().replace(';', ',') + 
                                            ',"UF":' + campos[2].inner_text().replace(';', ',') + '}')
        data.append('|'.join(instituicoes_parceiras))
    else:
        data.append("")
        
        
    # Indicadores de RH
    indicadores_rh = []
    rh = pagina.query_selector(f'tbody[id="idFormVisualizarGrupoPesquisa:j_idt404_data"]')
    if(rh != None):
        rh = rh.query_selector_all('tr')
        for item in rh:
            campos = item.query_selector_all('td')
            if len(campos) == 1:
                break
            indicadores_rh.append('{"Formação acadêmica":' + campos[0].inner_text() + 
                                       ',"Pesquisadores":' + campos[1].inner_text() + 
                                          ',"Estudantes":' + campos[2].inner_text() + 
                                            ',"Técnicos":' + campos[3].inner_text() + 
                                        ',"Estrangeiros":' + campos[4].inner_text() + 
                                               ',"Total":' + campos[5].inner_text() + '}')
        data.append('|'.join(indicadores_rh))
    else:
        data.append("")
        
        
        
    # link
    data.append(pagina.url)
    
    escreve_grupos(data, input)

#Iterar as paginas
def iterate_resultado_busca(pagina, contexto, input):
    # Criar arquivo csv em branco
    create_base_file(input)
    # Locate the ordered list element
    ol_element = pagina.query_selector(f'ul[id="idFormConsultaParametrizada:resultadoDataList_list"][class="ui-datalist-data"]')

    # Find all <li> elements within the ordered list
    li_elements = ol_element.query_selector_all('li')

    # Iterate over the <li> elements and print their text content
    for li_element in li_elements:
        # Abre curriculo em nova pagina
        with contexto.expect_page() as pagina_curriculo_info:
            li_element.query_selector_all('a')[0].click()            
            time.sleep(7)
        pagina_curriculo = pagina_curriculo_info.value
        pega_dados_curriculo(pagina_curriculo, input)            
        # Fecha curriculo
        pagina_curriculo.close()
        
#Realizar consulta a partir dos temas
def busca_curriculos(pagina, contexto, input):
    pagina.goto("http://dgp.cnpq.br/dgp/faces/consulta/consulta_parametrizada.jsf")
    time.sleep(load_time)
    
    # Preenche assunto
    pagina.fill('xpath=//*[@id="idFormConsultaParametrizada:idTextoFiltro"]', input)
    
    # Consulta por 'Linha de Pesquisa'
    #select_element = pagina.query_selector('#idFormConsultaParametrizada\\:unidAnalise')
    #select_element.select_option(value='4')
    
    # Selecionar busca em 'Repercussões do grupo'
    pagina.locator('xpath=//*[@id="idFormConsultaParametrizada:campos:3"]').check()
    
    # Busca
    pagina.locator('xpath=//*[@id="idFormConsultaParametrizada:idPesquisar"]').click()
    time.sleep(7)
    
    ########## Verificar se existe algum resultado ###############
    if pagina.query_selector('select.ui-paginator-rpp-options') == None:
        print('Nenhum resultado para a consulta:', input)
        return
    ##############################################################
    
    #Inserir elemento para 1000 itens por página
    pagina.eval_on_selector_all('select.ui-paginator-rpp-options', 'elementos => elementos[0].innerHTML += \'<option value="10000">10000</option>\';')
    
    select_element = pagina.query_selector('select.ui-paginator-rpp-options')
    select_element.select_option('10000')
    time.sleep(7)

    # Iterate nos resultados das buscas
    iterate_resultado_busca(pagina, contexto, input)
    
#Inicio da execução
def run(input):
    with sync_playwright() as playwright:
        tentativas = 0
        while True:
            try:
                # Cria navegador
                print(f"=== INICIANDO NOVA EXECUÇÃO: {input} ===", f"{input}.log")
                navegador = playwright.chromium.launch(headless=True)
                contexto = navegador.new_context()
                pagina = contexto.new_page()
                busca_curriculos(pagina, contexto, input)
                break
            except Exception as e: 
                tentativas+=1
                print(f"Tentativa: {tentativas} |\t{e}", f"{input}.log")
                navegador.close()


                
                
if __name__ == "__main__":
    #data = ["metaverso", "metaverse", "digital twin", "blockchain", "gemeos digitais", "Non-fungible Token",   "Realidade Aumentada", "Realidade Virtual", "Virtual Reality", "Augmented Reality", "Realidade Mista", "5G", "6G", "pos-5G", "Inteligencia Artificial", "Artificial Intelligence", "Contratos Inteligentes", "Smart Contracts", "Segurança Cibernética", "Cybersecurity"]

    data = ["fake news", "misinformation", "rumor", "disinformation", "desinformação"]

    # Iterate over the keys and create a thread for each key-value pair
    for input in data:
            run(input)
