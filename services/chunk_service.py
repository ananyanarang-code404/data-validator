# services/chunk_service.py

import io
import zipfile


class ChunkService:

    @staticmethod
    def split_dataframe(df, chunk_size):
        chunks = []

        for i in range(0, len(df), chunk_size):
            chunks.append(
                df.iloc[i:i + chunk_size]
            )

        return chunks

    @staticmethod
    def create_zip(chunks):
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(
            zip_buffer,
            "w",
            zipfile.ZIP_DEFLATED
        ) as zip_file:

            for idx, chunk in enumerate(chunks):

                zip_file.writestr(
                    f"cleaned_part_{idx + 1}.csv",
                    chunk.to_csv(index=False)
                )

        zip_buffer.seek(0)

        return zip_buffer