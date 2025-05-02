import csv
from io import StringIO


class FileGenerator:
    def __init__(self):
        pass

    async def generate_csv(self, headers, rows):
        """
        Generate a CSV file from headers and rows.
        """
        csv_data = StringIO()
        writer = csv.writer(csv_data)

        writer.writerow(headers)

        for row in rows:
            writer.writerow(row)

        csv_data.seek(0)
        return csv_data
