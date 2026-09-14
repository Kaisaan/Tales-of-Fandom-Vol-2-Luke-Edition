import sys, shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from libfandom.script import MSB_FILES
from tasks.from_sheets import from_sheets

def update_text():
    for msb in MSB_FILES:
        from_sheets(msb)
        print(f"Copying {msb}")

        shutil.copy(Path(f"decompiled/{msb}.msb"), Path(f"DVDDATA/adv/msb/{msb}.msb"))