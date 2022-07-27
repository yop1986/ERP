from datetime import datetime
from pathlib import Path

from django.conf import settings

#ESCRITURA DE LOGS
def _escribe_log(datos, nombre):
    ''' 
        Escritura de logs
            datos:  arreglo con la información a guardar en el archivo
            nombre: nombre del archivo
    '''
    output_file = Path(f'{settings.STATIC_ROOT}\\logs\\{nombre}.log')
    output_file.parent.mkdir(exist_ok=True, parents=True)
    f = open(output_file, 'a+')
    f.writelines([d+'\n' for d in datos])
    f.close()

    return output_file

#FUNCIONES DE CONVERSION
def _parse(valor, tipo, *args):
    '''
        _parse: convierte los valores que se importan de acuerdo con el tipo indicado
            valor:  es el valor que se debe convertir
            tipo:   corresponde al tipo de dato que se desea convertir (str, int, float, date, bool)
                    cualquier otro valor se devuelve del mismo tipo que el original
            args:   recibe todos los parametros para obtener información adicional {vacio, valores, default}
        Return: valor parseado al tipo deseado
    '''  
    if tipo=='str':
        return str(valor)
    elif tipo=='int':
        return _parse_int(valor)
    elif tipo=='float':
        return _parse_float(valor)
    elif tipo=='bool':
        # dentro de los parametros se define (en mayusculas y separado por |) los valores posibles
        return _parse_boolean(valor, args[0]['valores'].split('|')[0])
    elif tipo=='date':
        return _parse_datetime(valor)
    else:
        return valor

def _parse_int(valor, default=0):
    '''
        _parse_int: convierte, de ser posible, el valor a entero en caso contrario asigna valor default
            valor:  es el valor que se debe convertir
            default:valor por defecto en caso de error
        Return: valor convertido a entero
    '''  
    try:
        return int(valor)
    except Exception as e:
        return default

def _parse_float(valor, default=0):
    '''
        _parse_float: convierte, de ser posible, el valor a punto flotante en caso contrario asigna valor default
            valor:  es el valor que se debe convertir
            default:valor por defecto en caso de error
        Return: valor convertido a punto flotante
    '''  
    try:
        return valor if isinstance(valor, float) else float(valor)
    except Exception as e:
        return default

def _parse_boolean(valor, verdadero):
    if valor:
        return True if valor.upper()==verdadero else False
    else:
        return False #valor default

def _parse_datetime(valor, formato_ingreso="%d/%m/%Y", formato_egreso="%Y-%m-%d"):
    '''
        _parse_datetime: convierte, de ser posible, el valor a fecha
            valor:  es el valor que se debe convertir
            formato_ingreso: formato en que se ingresa la fecha
            formato_egreso: formato en que se devuelve
        Return: valor convertido a fecha
    '''  
    if isinstance(valor, datetime):
        return valor.strftime(formato_egreso)
    else:
        try:
            return datetime.strptime(valor, formato_ingreso).strftime(formato_egreso)
        except Exception as e:
            return ''
    

#LECTURA DE REGISTROS
def _lectura_registros(hoja, parametros, fila_encabezado=1):
    '''
        lectura_registros
            hoja: openpyxl.load_workbook, hoja del archivo leído
            parametros: diccionario llave valor de columnas y campos 
        Return: lista de listas con los registros
    '''  
    orden = {}
    for idxc, columna in enumerate(hoja[fila_encabezado]):
        if (not parametros or hoja[fila_encabezado][idxc].value in parametros):
            orden[idxc]=hoja[fila_encabezado][idxc].value

    lista = []
    excluidos = []
    for idxf, fila in enumerate(hoja.iter_rows(min_row=fila_encabezado+1)):
        try:
            registro = {}
            for idxc in orden:
                valor = fila[idxc].value
                if (valor and 'valores' in parametros[orden[idxc]] and not valor.replace(' ', '').upper() \
                    in parametros[orden[idxc]]['valores'].split('|')) or (not valor and not parametros[orden[idxc]]['vacio']):
                    #Si la columna no puede ser vacia, o si tiene valores definidos que no corresponden al valor ingresado
                    registro = None
                    excluidos.append(f"f:{idxf+1:6} >> {orden[idxc]}")
                    break
                registro[parametros[orden[idxc]]['equivalente']]=_parse(valor, parametros[orden[idxc]]['tipo'], parametros[orden[idxc]])
            if registro:
                lista.append(registro)
        except Exception as e:
            excluidos.append(f"f:{idxf+1:6} >> {orden[idxc]} (Validation Error)")
    #segmenta en grupos de 200
    return [lista[i:i + 200] for i in range(0, len(lista), 200)], excluidos 