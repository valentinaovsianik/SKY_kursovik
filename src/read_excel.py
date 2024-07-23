import pandas as pd

def read_excel_file(file_name: str):
    """Считывает данные из excel-файла и преобразовывает их в формат JSON"""
    try:
        df = pd.read_excel(file_name)
        return df.to_dict(orient="records")
    except Exception as e:
        raise RuntimeError(f"Ошибка при чтении файла {file_name}: {str(e)}")


if __name__ == "__main__":
    file_name = "../data/operations.xlsx"

    try:
        data = read_excel_file(file_name)
        print(data)
    except RuntimeError as e:
        print(e)
