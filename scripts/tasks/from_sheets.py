# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "google-api-python-client",
#     "google-auth",
# ]
# ///

"""
Pull latest translations from Google Sheets and apply them to wscript files.
"""

import csv
import os
import sys
import tempfile
from pathlib import Path

from google.oauth2 import service_account
from googleapiclient.discovery import build

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tasks.from_csv import from_csv

SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/spreadsheets",
]

SPREADSHEET_ID = "1HrBGYn7-8ASdDTNMNOLmLcHSeqfSY1V4FV89fN9I2z0"

SECRET_FILE = "fandom2_secret.json"
EXPECTED_HEADER = ["JP Speaker", "EN Speaker", "JP Text", "EN Text", "ID", "Comments"]


def get_rows(service, sheet):
    range_name = f"{sheet}!A:Z"
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=range_name)
        .execute()
    )
    return result.get("values", [])


def from_sheets(sheetName: str):
    if not os.path.exists(SECRET_FILE):
        sys.exit(
            f"{SECRET_FILE} not found. Make sure it's in the folder."
        )

    if not os.path.isdir("decompiled"):
        sys.exit(f"Directory decompiled does not exist")

    credentials = service_account.Credentials.from_service_account_file(
        SECRET_FILE, scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=credentials)

    rows = get_rows(service, sheetName)
    if not rows:
        sys.exit(f"No rows fetched from '{sheetName}' sheet")

    header = rows[0]
    if header[: len(EXPECTED_HEADER)] != EXPECTED_HEADER:
        print(header)
        sys.exit(
            "Header does not match expected: " + ",".join(EXPECTED_HEADER)
        )


    with tempfile.TemporaryDirectory() as tmp:

            msb_path = Path("decompiled") / sheetName


            csv_path = Path(tmp) / f"{Path(sheetName).stem}.csv"
            with csv_path.open("w", newline="", encoding="utf-8") as fp:
                writer = csv.writer(fp)
                writer.writerows(rows)

                


            print(f"Applying sheet translations to {msb_path}.msb")
            from_csv(str(msb_path), str(csv_path))

    


if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "decompiled"
    from_sheets(target_dir)