from flask import Flask, request, jsonify
import os
import platform
from datetime import datetime

app = Flask(__name__)

def obtener_informacion_archivos(direccion):
    informacion_archivos = []

    for root, dirs, files in os.walk(direccion):
        for filename in files:
            if not filename.startswith('~'):
                ruta_completa = os.path.join(root, filename)
                fecha_modificacion_timestamp = os.path.getmtime(ruta_completa)
                fecha_modificacion = formatear_fecha(fecha_modificacion_timestamp)
                version = obtener_version_archivo(ruta_completa)
                localizacion = plataforma_archivo(ruta_completa)

                informacion_archivos.append({
                    'nombre': filename,
                    'fecha_modificacion': fecha_modificacion,
                    'version': version,
                    'localizacion': localizacion
                })

    return informacion_archivos, len(informacion_archivos)

def obtener_version_archivo(ruta):
    try:
        # Obtener la versión del archivo (si es posible)
        if platform.system() == 'Windows':
            import win32api
            info_version = win32api.GetFileVersionInfo(ruta, "\\")
            version = f"{info_version['FileVersionMS']}.{info_version['FileVersionLS']}"
        else:
            import subprocess
            version = subprocess.check_output(["stat", "-c", "%Y", ruta]).decode().strip()
        
        return version
    except Exception as e:
        return None

def plataforma_archivo(ruta):
    # Normalizar la ruta para evitar barras invertidas duplicadas
    return os.path.normpath(os.path.dirname(ruta))

def formatear_fecha(timestamp):
    # Formatear la fecha en el formato deseado "dd/mm/YYYY HH:MM"
    fecha_objeto = datetime.fromtimestamp(timestamp)
    fecha_formateada = fecha_objeto.strftime("%d/%m/%Y %H:%M")
    return fecha_formateada

@app.route('/obtener_informacion_archivos', methods=['GET'])
def obtener_informacion_archivos_endpoint():
    try:
        # Obtenemos la dirección del explorador de archivos desde los parámetros de la solicitud
        direccion = request.args.get('direccion')

        # Validamos si la dirección existe y es un directorio
        if os.path.exists(direccion) and os.path.isdir(direccion):
            # Obtener información de los archivos de forma recursiva
            informacion_archivos, numero_elementos = obtener_informacion_archivos(direccion)
            respuesta = {
                'archivos': informacion_archivos,
                'numero_elementos': numero_elementos
            }
            return jsonify(respuesta)
        else:
            return jsonify({'error': 'La dirección no es válida o no es un directorio'}), 400
    except Exception as e:
        return jsonify({'error': f'Error interno: {str(e)}'}), 500

if __name__ == '__main__':
    # Ejecutamos el servidor en el puerto 5000
    app.run(debug=True, port=5000)
