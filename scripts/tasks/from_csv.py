import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from libfandom.script import make_msb



def from_csv(msb_file, csv_file):

    make_msb(msb_file, csv_file)



if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(
            "Usage: python scripts/tasks/from_csv.py <wscript_file> <csv_file> <out_wscript_file>"
        )
        sys.exit(1)
    from_csv(sys.argv[1], sys.argv[2])