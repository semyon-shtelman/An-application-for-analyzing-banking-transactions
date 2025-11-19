
import pandas as pd

def load_transactions_excel(excel_file_patch: str) -> list[dict]:
    try:
        df = pd.read_excel(excel_file_patch)
        transactions = df.to_dict(orient='records')
        return transactions
    except FileNotFoundError:
        print(f'error file {excel_file_patch} no find')
        return []
    except Exception as e:
        print(f'error read file Excel{e}')
        return []

