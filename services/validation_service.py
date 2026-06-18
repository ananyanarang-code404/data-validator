# services/validation_service.py

import pandas as pd

from validators.row_validator import validate_row


class ValidationService:

    @staticmethod
    def validate_dataframe(
        df,
        phone_rules,
        date_format
    ):
        valid_rows = []
        invalid_rows = []

        for _, row in df.iterrows():

            row_dict = row.to_dict()

            errors = validate_row(
                row_dict,
                phone_rules,
                date_format
            )

            if errors:
                row_dict["errors"] = "; ".join(errors)
                invalid_rows.append(row_dict)
            else:
                valid_rows.append(row_dict)

        return (
            pd.DataFrame(valid_rows),
            pd.DataFrame(invalid_rows)
        )