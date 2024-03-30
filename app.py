from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
from transformation.transform import *
import os

app = Flask(__name__)

# Configura una carpeta para los archivos subidos
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/', methods=['GET', 'POST'])
def behaviour():
    if request.method == 'POST':
        # Se asume que tu formulario HTML tiene campos adecuados para estos nombres
        table_file = request.files.get('tableFile')
        data_file = request.files.get('dataFile')
        output_path = request.form.get('outputPath')
        range_value = request.form.get('rangeValue')

        if table_file and data_file:
            table_file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(table_file.filename))
            data_file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(data_file.filename))
            table_file.save(table_file_path)
            data_file.save(data_file_path)

            # Aquí puedes invocar a transform o a transform_csv y transform_excel
            # dependiendo de la lógica específica que quieras aplicar
            #transform(table_file_path, data_file_path, output_path, range_value)

            return "Transformación completada exitosamente."

    return render_template('index.html')

if __name__ == '__main__':
    # Asegúrate de que la carpeta de uploads existe
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
