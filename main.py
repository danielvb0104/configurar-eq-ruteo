import requests
import pandas as pd
import numpy as np


def run():
    nombre_archivo = 'G:/Mi unidad/Coordinadora/Ruteo/Primera salida/ConfiguracionEquipos.xlsx'
    plataformas, equipos = importar_archivo_excel(nombre_archivo)

    # Para crear las plataformas
    for plataforma in plataformas:
        respuesta = realizar_peticion(plataforma, 'https://apiv2-test.coordinadora.com/ruteo/cm-visitas-ruteo-ms/nodo-fijo')
        print(respuesta)
    for equipo in equipos:
        respuesta = realizar_peticion(equipo,
                                      'https://apiv2-test.coordinadora.com/equipos/cm-equipos-ms/')
        print(respuesta)


def realizar_peticion(objeto, endpoint):
    response = requests.post(endpoint, json=objeto)
    json_response = response.json()
    return json_response


def obtener_plataformas(archivo_excel, nombre_hoja):
    df_plataformas = pd.read_excel(archivo_excel, nombre_hoja, dtype={'codigoCiudad': str})
    df_plataformas = df_plataformas.dropna(how='all')
    plataformas = [fila.to_dict() for i, fila in df_plataformas.iterrows()]
    dict_plataformas = {}
    for i in plataformas:
        i['latitud'] = round(i['latitud'], 13)
        i['longitud'] = round(i['longitud'], 13)
        if np.isnan(float(i['codigoCiudad'])):
            i['codigoCiudad'] = None
        dict_plataformas[i['nombre']] = i
    return plataformas, dict_plataformas


def obtener_configuracion_equipos_por_terminal(archivo_excel, nombre_hoja):
    df_configuracion = pd.read_excel(archivo_excel, nombre_hoja, dtype={'numeroMovil': str})
    df_configuracion = df_configuracion.dropna(how='all')
    config = {fila.to_dict()['terminal']: fila.to_dict() for i, fila in df_configuracion.iterrows()}
    for i in config.values():
        if np.isnan(float(i['numeroMovil'])):
            i['numeroMovil'] = None
    return config


def obtener_plataforma_por_equipo(archivo_excel, nombre_hoja):
    df_equipos = pd.read_excel(archivo_excel, nombre_hoja)
    df_equipos = df_equipos.dropna(how='all')
    equipos_plataformas = [fila.to_dict() for i, fila in df_equipos.iterrows()]
    return equipos_plataformas


def configurar_informacion_equipos(configuracion_por_terminal, equipos_plataformas, dict_plataformas):
    equipos = []
    for i in equipos_plataformas:
        equipo = configuracion_por_terminal[i['terminal']]
        if i['nombre_plataforma'] in dict_plataformas:
            plataforma = dict_plataformas[i['nombre_plataforma']]
            id_plataforma = str(plataforma['latitud']) + ',' + str(plataforma['longitud'])
            equipo['equipo'] = str(i['codigo_equipo'])
            equipo['idPlataformaInicio'] = id_plataforma
            equipo['idPlataformaFin'] = id_plataforma
            equipo['idRestaurante'] = id_plataforma
            equipo['tiempoInicio'] = str(equipo['tiempoInicio'])
            equipos.append(equipo)

    return equipos


def importar_archivo_excel(nombre_archivo):
    archivo_excel = pd.ExcelFile(nombre_archivo)
    nombre_hojas = {
        'plataforma_equipo': 'equipos',
        'plataformas': 'plataformas_logisticas',
        'configuracion_equipos': 'configuracion_equipos'
    }
    plataformas, dict_plataformas = obtener_plataformas(archivo_excel, nombre_hojas['plataformas'])
    configuracion_por_terminal = obtener_configuracion_equipos_por_terminal(
        archivo_excel, nombre_hojas['configuracion_equipos'])
    equipos_plataformas = obtener_plataforma_por_equipo(archivo_excel, nombre_hojas['plataforma_equipo'])
    equipos = configurar_informacion_equipos(configuracion_por_terminal, equipos_plataformas, dict_plataformas)

    return plataformas, equipos


if __name__ == '__main__':
    run()
