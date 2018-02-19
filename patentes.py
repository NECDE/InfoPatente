#!/usr/bin/python
#-*- coding:UTF-8 -*-

from bs4 import BeautifulSoup
import requests
import http.client
import urllib
import json
from imagesoup import ImageSoup

file = open('InfoPatente.txt','w')

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
	file.write(html)
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
		file.write('\n'+i[22:-5])
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
		file.write("Sin multas")
		return ("Sin multas")

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
	return respuesta

def runprogram():

	print ('''
	╔═══╗╔═══╗╔════╗╔═══╗╔═╗ ╔╗╔════╗╔═══╗╔═══╗
	║╔═╗║║╔═╗║║╔╗╔╗║║╔══╝║║╚╗║║║╔╗╔╗║║╔══╝║╔═╗║
	║╚═╝║║║ ║║╚╝║║╚╝║╚══╗║╔╗╚╝║╚╝║║╚╝║╚══╗║╚══╗
	║╔══╝║╚═╝║  ║║  ║╔══╝║║╚╗║║  ║║  ║╔══╝╚══╗║
	║║   ║╔═╗║  ║║  ║╚══╗║║ ║║║  ║║  ║╚══╗║╚═╝║
	╚╝   ╚╝ ╚╝  ╚╝  ╚═══╝╚╝ ╚═╝  ╚╝  ╚═══╝╚═══╝
				by @UnknDown
				 modded by NECDE
	''')
	patente = input("Ingrese Patente a consultar: ")
	print("\nPATENTE: " , patente.upper())
	file.write("\nPATENTE: "+patente.upper())
	try:
		url = "https://soap.uanbai.com/bci/soap/2018/ajax/loadPPU.jsp?PPU=%s&SES=DDB9674E703F9BB04C4F3BB2D96D8291.worker1" % patente
		peticion = requests.get(url)
		datos    = json.loads(peticion.content)

	except:
		print ("No se pudo obtener la información (SOAP)")
		file.write("No se pudo obtener la información (SOAP)")
		exit()

	# Datos del dueño
	
	nombredueño = (" Nombre: " + datos['propietario']['nombre'] + " " + datos['propietario']['ap_paterno'] + " " + datos['propietario']['ap_materno'])
	rutdueño = (" RUT: " + datos['propietario']['rut'] +"-" + datos['propietario']['dv'])
	
	print ("\n+--------- Datos del Dueño -------+")
	print(nombredueño)
	print(rutdueño)

	file.write ("\n\n+--------- Datos del Dueño -------+\n")
	file.write (nombredueño)
	file.write (rutdueño)

	# Datos del vehiculo
	
	tipovehi = (" Tipo: " + tipoVehiculo(datos['id_tipo']))
	marcavehi = (" Marca: " + datos['marca'])
	modelovehi = (" Modelo: "+ datos['modelo'])
	añovehi = (" Año: " + str(datos['ano']))
	nmotor = (" N° Motor: " + str(datos['vin']))
	dvpatente = (" DV patente: " + str(datos['dvpatente']))

	print("\n+--------- Datos del Vehiculo -------+")
	print(tipovehi+"\n"+marcavehi+"\n"+modelovehi+"\n"+añovehi+"\n"+nmotor+"\n"+dvpatente)

	file.write("\n\n+--------- Datos del Vehiculo -------+\n")
	file.write(tipovehi+"\n"+marcavehi+"\n"+modelovehi+"\n"+añovehi+"\n"+nmotor+"\n"+dvpatente)

	# Datos legales del vehiculo

	print ("\n+--------- Datos Legales -------+")
	file.write ("\n\n+--------- Datos Legales -------+\n")

	try:
		multastotales = str(multas_total(patente))
		print (" Total multas: " + multastotales)
		file.write ("\n\n Total multas: " + multastotales)
	except:
		print(" Error en acceso a datos de ServRegistroCivil")
		file.write("\nError en acceso a datos de ServRegistroCivil")

	# Verificamos si pertence al transporte publico
	publico = transportePublico(patente)
	print ("\n+--------- Datos transporte publico -------+")
	file.write("\n\n+--------- Datos transporte publico -------+")

	label    = []
	content  = []
	html     = BeautifulSoup(publico,"html5lib")
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
			file.write(" "+label[x]+": " + content[x])

		if content[total_content-2] != "":
			print (" Conductores: " + content[total_content-2])
			file.write(" Conductores: " + content[total_content-2])
		else:
			print (" Conductores: -")
			file.write(" Conductores: -")
	else:
		print (" El vehiculo no pertenece al transporte publico")
		file.write("\n\n El vehiculo no pertenece al transporte publico")
	file.close() 


	# Buscar-Descargar-Mostrar imagenes del vehiculo (google images)
	busqueda = datos['marca']+" "+datos['modelo']
	if len(busqueda) == 1:
		print("\nError consiguiendo datos de SOAP")
	else:
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

runprogram()