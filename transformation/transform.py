import pandas as pd

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

def transform_excel(file_path):
    """
    Lee un archivo Excel y lo convierte en un DataFrame de pandas.

    :param file_path: Ruta al archivo Excel.
    :return: DataFrame de pandas con los datos del archivo Excel.
    """
    try:
        df = pd.read_excel(file_path)
        # Aquí puedes agregar transformaciones específicas al DataFrame
        return df
    except Exception as e:
        print(f"Error al transformar el archivo Excel: {e}")
        return None
