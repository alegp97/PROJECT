
import pandas as pd
import uuid
import os

file_path = 'C:/Users/alegp/OneDrive/Escritorio/NEXTIMIZE/wetransfer_datos-binter_2024-04-05_1531/NACIONAL/Binter_RAW_DATA_Campaign_Manager_nacional&Internacional.xlsx'

df = pd.read_excel(file_path,
                    engine='openpyxl')

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


# Lista de columnas a conservar
columnas_deseadas = ['Site (CM360)', 'Placement', 'Impressions', 'Clicks', 'Date', 'Purchase activities : Binter Thank you Page: Total Conversions']

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
df_filtrado = df_filtrado.rename(columns={'Date': 'Mes', 'Site (CM360)': 'Site', 'Impressions':'Impresiones',
                                           'Purchase activities : Binter Thank you Page: Total Conversions' : 'Conversiones' })


# Limpiar la columna 'Impresiones', quitando cualquier carácter no numérico
df_filtrado['Impresiones'] = df_filtrado['Impresiones'].astype(str).str.replace(r'\D', '', regex=True)

# Convertir la columna 'Impresiones' a tipo entero
df_filtrado['Impresiones'] = pd.to_numeric(df_filtrado['Impresiones'], errors='coerce').fillna(0).astype(int)

# Repetir el proceso para la columna 'Clicks'
df_filtrado['Clicks'] = df_filtrado['Clicks'].astype(str).str.replace(r'\D', '', regex=True)
df_filtrado['Clicks'] = pd.to_numeric(df_filtrado['Clicks'], errors='coerce').fillna(0).astype(int)

# Convertir las columnas 'Site' y 'Placement' a tipo string
df_filtrado['Site'] = df_filtrado['Site'].astype(str)
df_filtrado['Placement'] = df_filtrado['Placement'].astype(str)

# Eliminamos las filas que contengan al menos un valor nulo
df_filtrado = df_filtrado.dropna()



# Definir el nombre del archivo basado en el nombre original u otra lógica
original_filename = os.path.basename(file_path)
unique_id = uuid.uuid4()
transformed_filename = f"Transformed_{unique_id}_{original_filename}"


output_folder = 'C:/Users/alegp/OneDrive/Escritorio/NEXTIMIZE/PROJECT/transformed'
# Construir la ruta completa
full_path = os.path.join(output_folder, transformed_filename)


CPM_POR_PLACEMENT_PATH = 'C:/Users/alegp/OneDrive/Escritorio/NEXTIMIZE/BINTER .xlsx'




# JOIN con el CPM por Placement
df_cpm_placement = pd.read_excel(CPM_POR_PLACEMENT_PATH, engine='openpyxl')
df_cpm_placement = df_cpm_placement.rename(columns={'SITE CM ': 'Site', 'PLACEMENT CM ':'Placement'})


df_join = pd.merge(df_filtrado, df_cpm_placement[['Site', 'Placement', 'CPM']], on=['Site', 'Placement'], how='inner')
# Calculamos la nueva columna 'Inversión'
df_join['Inversion'] = (df_join['Impresiones'] / 1000) * df_join['CPM']


df_join.to_excel(full_path, index=False, engine='openpyxl')
print(df_join.info())


#print(df_cpm_placement.info())

#df = pd.read_excel(tabla_cpm_path, engine='openpyxl')

