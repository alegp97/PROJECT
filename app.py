from flask import Flask, render_template, redirect, abort, request, send_from_directory, jsonify
from werkzeug.utils import secure_filename, safe_join
from transformation.transform import *

from version import __version__
import shutil
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'C:/Users/alegp/OneDrive/Escritorio/NEXTIMIZE/PROJECT/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

TRANSFORMED_FOLDER = 'C:/Users/alegp/OneDrive/Escritorio/NEXTIMIZE/PROJECT/transformed'  

TABLAS_CPM_FOLDER = 'C:/Users/alegp/OneDrive/Escritorio/NEXTIMIZE/PROJECT/tabla_soporte'
app.config['TABLAS_CPM_FOLDER'] = TABLAS_CPM_FOLDER

def delete_files_from_folder(FOLDER_PATH):
    # Borrar todos los archivos en FOLDER_PATH
    for filename in os.listdir(FOLDER_PATH):
        file_path = os.path.join(FOLDER_PATH, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))



@app.route('/', methods=['GET', 'POST'])
def upload_and_transform():
    transformed_files = ""
    if request.method == 'POST':
        files_to_transform = request.files.getlist('file')  # Obteniendo múltiples archivos a transformar
        tabla_cpm_file = request.files.get('tabla_cpm')  # Archivo "Tablas CPM"
        tabla_cpm_path = TABLAS_CPM_FOLDER
        cpm_placement_file = request.files.get('cpm_por_placement')  # Archivo "Tablas CPM"
        cpm_placement_file_path = TABLAS_CPM_FOLDER

        # Procesar el archivo "CPM_POR_PLACEMENT"
        if cpm_placement_file and cpm_placement_file.filename != '':
            cpm_placement_filename = secure_filename(cpm_placement_file.filename)
            cpm_placement_file_path = os.path.join(app.config['TABLAS_CPM_FOLDER'], cpm_placement_filename)
            cpm_placement_file.save(cpm_placement_file_path)

        # Procesar el archivo "Tablas CPM"
        if tabla_cpm_file and tabla_cpm_file.filename != '':
            tabla_cpm_filename = secure_filename(tabla_cpm_file.filename)
            tabla_cpm_path = os.path.join(app.config['TABLAS_CPM_FOLDER'], tabla_cpm_filename)
            tabla_cpm_file.save(tabla_cpm_path)
            

        # Transformar los archivos
        for file in files_to_transform:
            if file:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)

                # Llamada a transform excel
                output_message = transform_excel(file_path, 
                                                 CPM_POR_PLACEMENT_PATH=cpm_placement_file_path, 
                                                 tabla_cpm_path=tabla_cpm_path, 
                                                 output_folder=TRANSFORMED_FOLDER)
                
        transformed_files = os.listdir(TRANSFORMED_FOLDER)
        transformed_files = sorted(transformed_files, #listar por más recientes
                                   key=lambda x: os.path.getmtime(os.path.join(TRANSFORMED_FOLDER, x)), reverse=True)
    
        return jsonify({'files': transformed_files})

    transformed_files = os.listdir(TRANSFORMED_FOLDER)
    delete_files_from_folder(UPLOAD_FOLDER)
    return render_template('index.html', files=transformed_files, version=__version__)


@app.route('/download/<path:filename>')
def download_file(filename):
    return send_from_directory(TRANSFORMED_FOLDER, filename, as_attachment=True)

@app.route('/delete/<path:filename>')
def delete_file(filename):
    file_path = safe_join(TRANSFORMED_FOLDER, filename)
    try:
        os.remove(file_path)
        return redirect('/')
    except FileNotFoundError:
        abort(404)


import pandas as pd
@app.route('/preview/<path:filename>')
def preview_file(filename):
    # Asegurarse de que el archivo existe
    file_path = safe_join(TRANSFORMED_FOLDER, filename)
    if not os.path.exists(file_path) or not filename.endswith('.xlsx'):
        abort(404)
    try:
        # Utilizar pandas para leer el archivo Excel
        df = pd.read_excel(file_path)

        # Convertir el DataFrame a HTML y añadir estilos CSS para dar espacio entre las filas
        html = df.to_html(border=0, index=False)
        styled_html = f"""<style>
                            thead th {{text-align: left;}}
                            tbody tr {{border-bottom: 10px solid #ddd; padding-bottom: 11px;}}
                          </style>{html}"""
        return styled_html
    except Exception as e:
        return str(e)
    




if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    if not os.path.exists(TRANSFORMED_FOLDER):
        os.makedirs(TRANSFORMED_FOLDER)
    if not os.path.exists(TABLAS_CPM_FOLDER):
        os.makedirs(TABLAS_CPM_FOLDER)



    app.run(debug=True)