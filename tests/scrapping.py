#Verificando que el WebDriver estaba funcionando
# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options

# options = Options()
# options.headless = True

# service = Service("/usr/bin/chromedriver")

# driver = webdriver.Chrome(service=service, options=options)

# driver.get("https://google.com/")
# print(driver.title)
# driver.quit()


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, StaleElementReferenceException,NoSuchElementException
from bs4 import BeautifulSoup
from datetime import datetime
import time
import json
import uuid 

def get_webdriver():
    options = Options()
    options.headless = True
    service = Service("/usr/bin/chromedriver")

    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrapping(sujeto,codigo_cedula):

    procesos = []
    #nombre para cada archivo usando cedula/codigo/rut y fecha
    # Formatear la fecha y hora
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    #numero de identificacion aleatorio para garantizar que se sobrescriban los archivos
    unique_id = uuid.uuid4().hex

    nombre_archivo = f"{codigo_cedula}_{timestamp}_{unique_id}.json"

    def wait_for_loading_overlay_to_disappear(driver, timeout=20):
        try:
            WebDriverWait(driver, timeout).until(
                EC.invisibility_of_element_located((By.CLASS_NAME, 'loading-overlay'))
            )
        except TimeoutException:
            print("Loading overlay did not disappear in time")

    try:
        service = Service("/usr/bin/chromedriver")
        driver = get_webdriver()

        # Abrir la página web
        driver.get('https://procesosjudiciales.funcionjudicial.gob.ec/busqueda-filtros')

        # Esperar a que la página cargue completamente
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, sujeto)))

        # Ingresar el código de búsqueda en el campo correspondiente
        input_field = driver.find_element(By.CSS_SELECTOR, sujeto)
        input_field.send_keys(codigo_cedula)

        # Esperar un momento después de ingresar el código
        time.sleep(2)

        # Esperar a que el botón de búsqueda esté habilitado y hacer clic
        buscar_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Enviar formulario"]'))
        )
        buscar_btn.click()

        # Esperar a que la página de resultados cargue
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'cuerpo')))

        # Encontrar todos los enlaces de los iconos para los movimientos del proceso

        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[aria-label*="Vínculo para ingresar a los movimientos del proceso"]')))
        detalles_page = driver.page_source
        # Usar BeautifulSoup para analizar el HTML de la página de detalles
        total_paginas = 0
        #En ocasiones cuando la pagina carga por primera vez no aparece el numero total de paginas
        #solo hace falta recargar la pagina una vez para obtener el total de paginas
        #aun asi le damos 5 intentos por si acaso
        # for _ in range(10):
        #     try:
        #         wait_for_loading_overlay_to_disappear(driver)
        #         WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'mat-mdc-paginator-range-label')))
        #         soup = BeautifulSoup(detalles_page, 'html.parser')
        #         paginas_page = soup.find('div', class_='mat-mdc-paginator-range-label').text.strip()
        #         partes = paginas_page.split()
        #         total_paginas = int(partes[-1])
        #         print("paginas totales: ",total_paginas)
        #         #caso_numero = 1
        #         break
        #         #print("llegue aqui")
        #     except (AttributeError,TimeoutException) as e:
        #         print("intente refrescar")
        #         driver.refresh()

        sigo = [True]
        pagina = 0
        # for pagina in range(total_paginas):
        while sigo[0]:
            try:
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[aria-label*="Vínculo para ingresar a los movimientos del proceso"]')))
                icon_links = driver.find_elements(By.CSS_SELECTOR, 'a[aria-label*="Vínculo para ingresar a los movimientos del proceso"]')
                #print("cantidad de links",len(icon_links))
                for i in range(len(icon_links)):
                    #la cantidad de links debe ser tomada luego de pasar pagina
                    #len(icon_links)
                    #Cuando se esten sacando procesos de paginas que no sean al 1 aqui debe volverse a cambiar de pagina
                    #Tantas veces sea necesario
                    #print("item: ",i,"pagina: ",pagina)
                    for x in range(pagina):
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Página siguiente"]')))
                        wait_for_loading_overlay_to_disappear(driver)
                        try:
                            #WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[aria-label="Página siguiente"]')))
                            boton_siguiente_tanda = WebDriverWait(driver, 10).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Página siguiente"]'))
                                )
                            boton_siguiente_tanda.click()
                            time.sleep(1)

                        except (TimeoutException, NoSuchElementException):
                            # Si no se puede hacer clic en el botón "Siguiente", salir del bucle
                            json_string = json.dumps(procesos, indent=4)
                            with open(nombre_archivo, 'w') as json_file:
                                json.dump(procesos, json_file, indent=4)
                            print("No hay más páginas disponibles o no se puede hacer clic en el botón. Cuando intenta cambiar para acceder a la pagina X")
                            break
                        
                    wait_for_loading_overlay_to_disappear(driver)
                    #Esperar a que carguen los iconos
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[aria-label*="Vínculo para ingresar a los movimientos del proceso"]')))
                    # Volver a encontrar todos los icon_links para evitar StaleElementReferenceException
                    icon_links = driver.find_elements(By.CSS_SELECTOR, 'a[aria-label*="Vínculo para ingresar a los movimientos del proceso"]')
                    #print("cantidad de icon links",len(icon_links))
                    #Sacar el numero del caso

                    detalles_lista_incidentes = driver.page_source
                    soup_lista_incidentes = BeautifulSoup(detalles_lista_incidentes, 'html.parser')
                    caso = {}
                    numero_caso = soup_lista_incidentes.find_all('div', class_='id')
                    #print("Cantidad de casos",len(numero_caso))
                    #si el valor de i es mayor a la cantidad de casos, salirse del bucle
                    if i == len(numero_caso):
                        #print("llegue aqui, al break")
                        sigo[0] = False
                        #print(sigo)
                        break
                    caso['caso'] = numero_caso[i].text.strip()
                    #caso_numero = caso_numero + 1
                    #print("caso_numero_contando: ", caso_numero)
                    # Hacer clic en el icon_link actual
                    icon_links[i].click()
                    # Esperar a que el enlace para ingresar al incidente esté presente
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[aria-label*="ingresar al incidente"]')))
                    #resulta que algunos casos pueden tener varios incidentes, por lo tanto 
                    #hay que hacer que entre a todos los incidentes
                    incidentes = []
                    incidentes_link = driver.find_elements(By.CSS_SELECTOR, 'a[aria-label*="ingresar al incidente"]')
                    for j in range(len(incidentes_link)):
                        # Hacer clic en el enlace para ingresar al incidente
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'a[aria-label*="ingresar al incidente"]')))
                        incidentes_inner_link = driver.find_elements(By.CSS_SELECTOR, 'a[aria-label*="ingresar al incidente"]')
                        incidentes_inner_link[j].click()
                        wait_for_loading_overlay_to_disappear(driver)
                        # Esperar a que la página de detalles cargue completamente
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'filtros-busqueda')))
                        #Hacer clic en el boton de ampliar detalles
                        wait_for_loading_overlay_to_disappear(driver)
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button[class="mdc-button mat-mdc-button mat-unthemed mat-mdc-button-base"]')))
                        ampliar_btn = driver.find_element(By.CSS_SELECTOR, 'button[class="mdc-button mat-mdc-button mat-unthemed mat-mdc-button-base"]')
                        ampliar_btn.click()
                        # Extraer el HTML de la página de detalles
                        detalles_page_source = driver.page_source
                        # Usar BeautifulSoup para analizar el HTML de la página de detalles
                        detalles_soup = BeautifulSoup(detalles_page_source, 'html.parser')
                        # Encontrar la sección que contiene todos los datos
                        sections = detalles_soup.find_all('section', class_='filtros-busqueda')
                        # Inicializar un diccionario para almacenar los datos del proceso
                        datos_proceso = {}
                        for section in sections:
                            # Encontrar todos los divs dentro de la sección
                            divs = section.find_all('div')
                            for div in divs:
                                strong_elements = div.find_all('strong')
                                span_elements = div.find_all('span')
                                for strong, span in zip(strong_elements, span_elements):
                                    strong_text = strong.get_text(strip=True)
                                    span_text = span.get_text(strip=True)
                                    datos_proceso[strong_text] = span_text
                        datos_proceso['actuaciones_judiciales'] = []
                        actuaciones_judiciales = detalles_soup.find_all('mat-expansion-panel')
                        #print(actuaciones_judiciales)
                        for actuacion_judicial in actuaciones_judiciales:
                            fecha_element = actuacion_judicial.find('div', class_='cabecera-tabla')
                            titulo_element = actuacion_judicial.find('span', class_='title')
                            texto_element = actuacion_judicial.find('article', class_='actividad')
                            if fecha_element:
                                fecha = fecha_element.find('span').text.strip()
                            else:
                                fecha = ""
                            if titulo_element:
                                titulo = titulo_element.text.strip()
                            else:
                                titulo = ""
                            if texto_element:
                                texto = texto_element.text.strip()
                            else:
                                texto = ""
                            datos_proceso['actuaciones_judiciales'].append(
                                {
                                'fecha': fecha,
                                'titulo': titulo,
                                'texto': texto
                            })
                        incidentes.append(datos_proceso)
                        # Navegar de regreso a la página de incidentes
                        driver.back()
                        wait_for_loading_overlay_to_disappear(driver)
                        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'cuerpo')))
                    caso['incidentes'] = incidentes
                    procesos.append(caso)
                    # Navegar de regreso a la página de resultados
                    driver.back()
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'cuerpo')))
                    # Esperar un momento después de volver atrás
                    time.sleep(1)
                    wait_for_loading_overlay_to_disappear(driver)
                pagina = pagina + 1

            except (TimeoutException, NoSuchElementException):
                # Si no se encuentra el botón o no se puede hacer clic, salir del bucle
                print("No hay más páginas disponibles o no se puede hacer clic en el botón.")
                # Guardando los datos en un archivo Json
                json_string = json.dumps(procesos, indent=4)
                with open(nombre_archivo, 'w') as json_file:
                    json.dump(procesos, json_file, indent=4)
                break
            except WebDriverException as e:
                print(f"WebDriverException: {e.msg}", "algo fallo por aqui")
            #print(f"Valor de sigo después de la condición: {sigo}")
            if not(sigo[0]):
                break

        # Guardando los datos en un archivo Json
        json_string = json.dumps(procesos, indent=4)
        with open(nombre_archivo, 'w') as json_file:
            json.dump(procesos, json_file, indent=4)

    except TimeoutException as e:
        print("Error: Timeout waiting for page to load.")
    except WebDriverException as e:
        # Guardando los datos en un archivo Json
        json_string = json.dumps(procesos, indent=4)
        with open(nombre_archivo, 'w') as json_file:
            json.dump(procesos, json_file, indent=4)
        print(f"WebDriverException: {e.msg}","algo fallo de forma general")
    finally:
        driver.quit()


