import pandas as pd
import uuid
import datetime
import os

def transform_csv(file_path):
    """
    Lee un archivo CSV y lo convierte en un DataFrame de pandas.

    :param file_path: Ruta al archivo CSV.
    :return: DataFrame de pandas con los datos del archivo CSV.
    """
    try:
        df = pd.read_csv(file_path)
        # Aquí puedes agregar transformaciones específicas al DataFrame
        return df
    except Exception as e:
        print(f"Error al transformar el archivo CSV: {e}")
        return None
    

def preprocessCPMfile(cpm_file_path):
    """
    Procesa el archivo Excel CPM antes de realizar el join.
    
    :param cpm_file_path: Ruta al archivo Excel CPM que será procesado.
    :return: DataFrame con las columnas renombradas y listas para ser usadas en un join.
    """
    # Leer el archivo Excel utilizando 'openpyxl' como motor porque soporta archivos .xlsx
    df_cpm = pd.read_excel(cpm_file_path, engine='openpyxl')
    # Renombrar las columnas para eliminar espacios adicionales y asegurar consistencia
    df_cpm = df_cpm.rename(columns=lambda x: x.strip().replace('SITE CM', 'Site').replace('PLACEMENT CM', 'Placement'))
    # Convertir la columna 'CPM' a tipo float, asegurando que los datos sean adecuados para operaciones matemáticas
    if 'CPM' in df_cpm.columns:
        df_cpm['CPM'] = pd.to_numeric(df_cpm['CPM'], errors='coerce')
        df_cpm['CPM'].fillna(0, inplace=True)  # Opcional: reemplazar NaN por 0 si hay valores no convertibles

    # agregar aquí cualquier otro preprocesamiento necesario
    
    return df_cpm
    

def transform_excel(file_path, CPM_POR_PLACEMENT_PATH, tabla_cpm_path, output_folder):

    """
    Lee un archivo Excel, realiza transformaciones especificadas y guarda el resultado.

    :param file_path: Ruta al archivo Excel que será transformado.
    :param output_folder: Carpeta de destino para el archivo transformado.
    :return: Ruta al archivo transformado o mensaje de éxito/error.
    """

    try:
        
        df = pd.read_excel(file_path, engine='openpyxl') # lectura

        ############################ PARTE PREPROCESADO CABECERAS ############################

        # Buscamos el índice de la primera fila que contenga "report fields" en alguna de sus celdas
        idx = df.index[df.apply(lambda row: row.astype(str).str.contains('Report Fields').any(), axis=1)].tolist()

        # Si encontramos al menos un índice, eliminamos todas las filas anteriores
        if idx:
            first_idx = idx[0]  # Tomamos el primer índice que contenga "report fields"
            df_cleaned = df.iloc[first_idx+1:]  # Eliminamos todas las filas anteriores a "report fields"
        else:
            df_cleaned = df  # Si no encontramos "report fields", dejamos el DataFrame como está

        # Reestablecer los nombres de las columnas con los valores de la segunda fila (índice 1 porque estamos en base 0)
        df_cleaned.columns = df_cleaned.iloc[0]

        # Eliminar la primera fila, que ahora es redundante ya que sus valores se usaron como nombres de columna
        df_cleaned = df_cleaned[1:]

        # Restablecer el índice del DataFrame para corregir la secuencia después de eliminar filas
        df_cleaned.reset_index(drop=True, inplace=True)

        ############################ PARTE PREPROCESADO ############################
         # Normalizar los nombres de las columnas relacionadas con 'Active View:'
        df_cleaned.columns = [col.replace('Active View: ', '') for col in df_cleaned.columns]

        # Lista de columnas a conservar
        columnas_deseadas = ['Site (CM360)', 
                             'Placement', 
                             'Impressions', 
                             'Clicks', 
                             'Date', 
                             'Viewable Impressions',
                             'Measurable Impressions',
                             'Click-through Conversions',
                             'View-through Conversions']

        # Filtrar el DataFrame para conservar solo las columnas deseadas que existen en el DataFrame
        df_filtrado = df_cleaned[[col for col in columnas_deseadas if col in df_cleaned.columns]].copy()

        # Convertir la columna 'Date' al tipo datetime de pandas
        df_filtrado['Date'] = pd.to_datetime(df_filtrado['Date'], errors='coerce')

        # Diccionario de los nombres de los meses en inglés a español
        meses_espanol = {
            1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
            5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
            9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
        }

        # Reemplazo el valor de cada fecha por el nombre del mes en español
        df_filtrado['Date'] = df_filtrado['Date'].dt.month.map(meses_espanol)

        # Renombre de las columnas de los campos
        df_filtrado = df_filtrado.rename(columns={'Date': 'Mes', 'Site (CM360)': 'Site', 'Impressions':'Impresiones'})


        # Limpiar la columna 'Impresiones', quitando cualquier carácter no numérico
        df_filtrado['Impresiones'] = df_filtrado['Impresiones'].astype(str).str.replace(r'\D', '', regex=True)

        # Convertir la columna 'Impresiones' a tipo entero
        df_filtrado['Impresiones'] = pd.to_numeric(df_filtrado['Impresiones'], errors='coerce').fillna(0).astype(int)
        # Repetir el proceso para las columnas 'Clicks', 'Active view: Viewable Impressions',
          #                   'Active view: Measurable Impressions',
          #                  'Click-through Conversions',
          #                   'View-through Conversions'
        def clean_and_convert_column(df, column_name):
            # Eliminar caracteres no numéricos y convertir a int
            df[column_name] = df[column_name].astype(str).str.replace(r'\D', '', regex=True)
            df[column_name] = pd.to_numeric(df[column_name], errors='coerce').fillna(0).astype(int)

        columns_to_clean = [
            'Clicks', 
            'Viewable Impressions',
            'Measurable Impressions',
            'Click-through Conversions',
            'View-through Conversions',
            'Impresiones'
        ]
        for column in columns_to_clean:
            clean_and_convert_column(df_filtrado, column)

        # Convertir las columnas 'Site' y 'Placement' a tipo string
        df_filtrado['Site'] = df_filtrado['Site'].astype(str)
        df_filtrado['Placement'] = df_filtrado['Placement'].astype(str)

        # Eliminamos las filas que contengan al menos un valor nulo
        df_filtrado = df_filtrado.dropna()

        ############################ PARTE CALCULOS AÑADIDOS Y JOIN ############################
        # JOIN con el CPM por Placement
        df_cpm_placement = preprocessCPMfile(CPM_POR_PLACEMENT_PATH)
        df_join = pd.merge(df_filtrado, df_cpm_placement[['Site', 'Placement', 'CPM']], on=['Site', 'Placement'], how='inner')


        # Calculamos la nueva columna 'Inversión'
        df_join['Inversion'] = (df_join['Impresiones'] / 1000) * df_join['CPM']

        # Añadir calculo de una columna 'Total Binter Conversiones'
        df_join['Total Binter Conversiones'] = (df_join['Click-through Conversions'] + df_join['View-through Conversions'])
        # CPA – lo calcularemos dividiendo la Inversión/ Total Binter Thank you Page (Suma de Conversiones post click + post view).
        # + manejo de division por cero
        df_join['CPA'] = df_join.apply(lambda x: x['Inversion'] / x['Total Binter Conversiones'] 
                                       if x['Total Binter Conversiones'] > 0 else 0, axis=1)

        # Viewability – hay que calcularlo con las métricas Viewable Impressions/ Measurable Impressions
        # asegurando que no haya división por cero
        df_join['Viewability'] = df_join['Viewable Impressions'] / df_join['Measurable Impressions']
        df_join['Viewability'].fillna(0, inplace=True)  # En caso de NaN resultante de división por cero

        ############################ PARTE RENOMBRE Y GUARDADO ############################
        # Definir el nombre del archivo basado en el nombre original u otra lógica
        # ( id al final, + marca de tiempo delante del id, Binter_Nacional_Internacional )

        base_filename = 'Binter_Nacional_Internacional' #os.path.basename(file_path)

        unique_id = uuid.uuid4()
        current_timestamp = datetime.datetime.now().strftime("%H'%M''%S'''_%d-%m-%Y")

        transformed_filename = f"Transformed_{base_filename}_{current_timestamp}_{unique_id}.xlsx"

        # Construir la ruta completa
        full_path = os.path.join(output_folder, transformed_filename)

        # GUARDADO DEL ARCHIVO
        try:
            if not os.path.exists(output_folder):
                print("La carpeta no existe.")

            df_join.to_excel(full_path, index=False, engine='openpyxl')
            return f"Archivo transformado guardado exitosamente en {output_folder}"
        except Exception as e:
            return f"Error al guardar el archivo: {e}"
    


    except Exception as e:
        return f"Error al transformar el archivo Excel: {e}"





