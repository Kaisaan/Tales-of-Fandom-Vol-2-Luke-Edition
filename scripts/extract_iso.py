# /// script
# requires-python = ">=3.10"
# dependencies = [
# ]
# ///
import os
import shutil
import subprocess
import sys
from pathlib import Path



sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from libfandom.archive import unpack
from libfandom.script import extract_text
#from scripts.tasks.extract_graphics import extract_all_graphics


def main():

    extract_text()
    exit()

    if os.path.exists("extracted"):
        shutil.rmtree("extracted")
    print("Extracting ISO...")
    source_iso = Path("luke.iso")
    if not source_iso.exists():
        sys.stderr.write(f"Source ISO not found: {source_iso}\n")
        sys.exit(1)
    result = subprocess.run(
        ["dumps2iso", "-o", "extracted", "-x", "luke.xml", source_iso],
        capture_output=True,
        text=True,
        shell=False,
    )
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.returncode != 0:
        sys.stderr.write(
            f"dumps2iso failed with return code {result.returncode}\n"
        )
        if result.stderr:
            sys.stderr.write(f"stderr:\n{result.stderr}\n")
        sys.exit(result.returncode)

    # Copy extracted to translated
    if os.path.exists("translated"):
        shutil.rmtree("translated")
    shutil.copytree("extracted", "translated")
    print("Done!")

    print("Unpacking DVDDATA...")
    unpack("DVDDATA")
    print("Done!")

    print("Unpacking BGM...")
    unpack("BGM")
    print("Done!")

    print("Unpacking VOICE...")
    unpack("VOICE")
    print("Done!")

    print("Extracting script files into .csv files...")
    if os.path.exists("csv"):
        shutil.rmtree("csv")
    os.makedirs("csv", exist_ok=True)
    extract_text()
    print("Done!")


    print("Extracting graphics...")
    #extract_all_graphics()
    print("Done!")



if __name__ == "__main__":
    main()