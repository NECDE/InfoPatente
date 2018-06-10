from bs4 import BeautifulSoup
import requests
import http.client
import urllib
import json
from imagesoup import ImageSoup
import sys


def tipoVehiculo(numero):

	if numero == "1":
		tipo = 'AUTOMOVIL'
	elif numero == "2":
		tipo = 'STATION WAGON'
	elif numero == "3":
		tipo = 'TODO TERRENO'
	elif numero == "4":
		tipo = 'CAMIONETA'
	elif numero == "5":
		tipo = 'FURGON'
	elif numero == "7":
		tipo = 'CARRO DE ARRASTRE'
	elif numero == "12":
		tipo = 'MOTOCICLETA'
	else:
		tipo = 'Otro'

	return tipo

def imagenes_google(marca,modelo,ano):
	# BUSQUEDA DE IMAGENES DEL MODELO DEL AURO EN GOOGLE

	busqueda = marca+modelo+ano

	if len(busqueda) == 1:
		print("\nError consiguiendo datos de SOAP")
	elif len(sys.argv) >= 3:
		try:
			auto = ImageSoup()
			images = auto.search(busqueda, n_images=5)
			firstimage = images[0]
			secondimage = images[1]
			thirdimage = images[2]
			firstimage.show()
			secondimage.show()
			thirdimage.show()
		except:
			print("Error en busqueda de imagen de vehiculo")
	else:
		pass

def datos_persona_auto():

	try:
		url = "https://soap.uanbai.com/bci/soap/2018/ajax/loadPPU.jsp?PPU=%s&SES=DDB9674E703F9BB04C4F3BB2D96D8291.worker1" % patente
		peticion = requests.get(url)
		datos    = json.loads(peticion.content)

	except:
		print ("\nNo se pudo obtener la información (SOAP)")

	# Datos del dueño
	
	nombredueno = (" Nombre: " + datos['propietario']['nombre'] + " " + datos['propietario']['ap_paterno'] + " " + datos['propietario']['ap_materno'])
	rutdueno = (" RUT: " + datos['propietario']['rut'] +"-" + datos['propietario']['dv'])
	
	print ("\n+--------- Datos del Dueño -------+")
	print(nombredueno)
	print(rutdueno)

	# Datos del vehiculo
	
	tipovehi = (" Tipo: " + tipoVehiculo(datos['id_tipo']))
	marcavehi = (" Marca: " + datos['marca'])
	modelovehi = (" Modelo: "+ datos['modelo'])
	anoauto = (" Año: " + str(datos['ano']))
	nmotor = (" N° Motor: " + str(datos['vin']))
	dvpatente = (" DV patente: " + str(datos['dvpatente']))

	print("\n+--------- Datos del Vehiculo -------+")
	print(tipovehi+"\n"+marcavehi+"\n"+modelovehi+"\n"+anoauto+"\n"+nmotor+"\n"+dvpatente)

	# Imagenes del auto en google

	if len(sys.argv) >= 3 and sys.argv[3] == "-i" or "images":
		imagenes_google(datos['marca'],datos['modelo'],datos['ano'])
	else:
		print("\nNo mostrando imagenes")

def multas_total(patente):

	link       = "http://consultamultas.srcei.cl/ConsultaMultas/buscarConsultaMultasExterna.do"
	host       = "consultamultas.srcei.cl"
	parametros = 'ppu=%s' % patente
	headers    = {'Content-Type':'application/x-www-form-urlencoded','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8','User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:46.0) Gecko/20100101 Firefox/46.0','Cookie':'JSESSIONID=32F21D2C90883C05DEA350CBA98E1CDD'}
	conexionmultas   = http.client.HTTPConnection(host)

	conexionmultas.request("POST", link, parametros, headers)
	request    = conexionmultas.getresponse()
	respuesta  = request.read()
	conexionmultas.close()
	html       = BeautifulSoup(respuesta,"html5lib")
	entradas   = html.find_all('div', {'class':'textEncabezadoTablaVentas'})
	final      = []

	# SACANDO MULTAS DE LA PAGINA 
	def has_six_characters(css_class):
		return css_class is not None and len(css_class) == 9

	multass = html.find_all('td',class_=has_six_characters)
	doblemultas = len(multass)
	totalmultas = doblemultas // 2
	contador=0
	paragraphs = []
	for x in multass:
		paragraphs.append(str(x))

	for i in paragraphs:
		print(i[22:-5])
		contador+=1
		if contador == totalmultas:
			break
		else:
			pass

	for item in entradas:
		item.encode('utf-8')
		resultado  = item.getText()
		final.append(resultado)

	if len(final) > 0:
		return final[0]
	else:
		print ("Sin multas")

	try:
		multastotales = str(multas_total(patente))
		print (" Total multas: " + multastotales)
	except:
		print(" Error en acceso a datos de ServRegistroCivil")

def transportePublico(patente):

	urlPublico      = "http://apps.mtt.cl/consultaweb/default.aspx"
	peticionPublico = requests.get(urlPublico)
	htmlPublico     = BeautifulSoup(peticionPublico.content ,"html5lib")

	state           = htmlPublico.find('input',{'name':'__VIEWSTATE'}).get('value')
	validation      = htmlPublico.find('input',{'name':'__EVENTVALIDATION'}).get('value')
	parametros_publicos = urllib.parse.urlencode({'__VIEWSTATE':state,'__EVENTVALIDATION':validation,'ctl00$MainContent$btn_buscar':'Buscar','ctl00$MainContent$ppu':patente})

	headers   = {'Content-Type':'application/x-www-form-urlencoded','User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:58.0) Gecko/20100101 Firefox/58.0','Cookie':'PHPSESSID=5905d3b7cb7bf267d6430a8685b4f776','Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
	conexiontranspublic   = http.client.HTTPConnection('apps.mtt.cl')
	conexiontranspublic.request("POST", "http://apps.mtt.cl/consultaweb/default.aspx", parametros_publicos, headers)
	request   = conexiontranspublic.getresponse()
	respuesta = request.read()
	conexiontranspublic.close()

	print ("\n+--------- Datos transporte publico -------+")

	label    = []
	content  = []
	html     = BeautifulSoup(respuesta,"html5lib")
	entradas = html.find_all('td', {'class':'label'})
	cont     = html.find_all('span')

	for item in entradas:
		item.encode('utf-8')
		resultado = item.getText()
		label.append(resultado)

	for contenido in cont:
		contenido.encode('utf-8')
		resultados  = contenido.getText()
		content.append(resultados)

	content.pop(0)
	total_label   = len(label)
	total_content = len(content)

	# verificamos si encuentra datos en transporte publico
	if total_label > 0:
		for x in range(0,total_label):
			print (" "+label[x]+": " + content[x])

		if content[total_content-2] != "":
			print (" Conductores: " + content[total_content-2])
		else:
			print (" Conductores: -")
	else:
		print (" El vehiculo no pertenece al transporte publico")

def runprogram():
	print ('''\n\n
	╔═══╗╔═══╗╔════╗╔═══╗╔═╗ ╔╗╔════╗╔═══╗╔═══╗
	║╔═╗║║╔═╗║║╔╗╔╗║║╔══╝║║╚╗║║║╔╗╔╗║║╔══╝║╔═╗║
	║╚═╝║║║ ║║╚╝║║╚╝║╚══╗║╔╗╚╝║╚╝║║╚╝║╚══╗║╚══╗
	║╔══╝║╚═╝║  ║║  ║╔══╝║║╚╗║║  ║║  ║╔══╝╚══╗║
	║║   ║╔═╗║  ║║  ║╚══╗║║ ║║║  ║║  ║╚══╗║╚═╝║
	╚╝   ╚╝ ╚╝  ╚╝  ╚═══╝╚╝ ╚═╝  ╚╝  ╚═══╝╚═══╝
				by @UnknDown
				 modded by NECDE
	''')
	
	print("\nPATENTE: " , patente.upper())

	# DATOS PERSONA Y AUTO
	try:
		datos_persona_auto()
	except:
		print(" Error obteniendo datos personales y del auto")

	# DATOS LEGALES
	print ("\n+--------- Datos Legales -------+")
	try:
		multas_total(patente)
	except:
		print(" Error obteniendo multas")

	# DATOS SI ES TRANSPORTE PUBLICO
	transportePublico(patente)

if len(sys.argv) >= 2:
	patente = sys.argv[1]
else:
	print("""Usage: python patentes.py aabb11 -i
""")
if len(sys.argv) >= 2 and len(sys.argv[1]) == 6:
	runprogram()
else:
	print("\n Ingresa una patente con 6 valores alfanumericos\n")