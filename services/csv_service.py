
import pandas as pd


class CSVService:

    @staticmethod
    def load_csv(uploaded_file):
        try:
            return pd.read_csv(uploaded_file)
        except Exception as e:
            raise Exception(
                f"Failed to read CSV: {str(e)}"
            )

    @staticmethod
    def export_csv(df):
        return df.to_csv(index=False).encode("utf-8")