import json
import pandas as pd


def load_transactions_excel(excel_file_patch: str) -> pd.DataFrame | list:
    try:
        df = pd.read_excel(excel_file_patch)
        return df
    except FileNotFoundError:
        print(f"error file {excel_file_patch} no find")
        return []
    except Exception as e:
        print(f"error read file Excel{e}")
        return []


def load_json_file(json_file_patch: str):
    with open(json_file_patch, "r", encoding="utf-8") as json_file:
        return json.load(json_file)
