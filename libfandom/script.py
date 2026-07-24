import csv
from pathlib import Path

MSB_FILES = ["mlist_00topa", "mlist_01tosa", "mlist_02toaa", "mlist_03toab", "mlist_04tofa", "mlist_05tope", "mlist_06tetc"]
MSB_MAGIC = b"MSB!\x09\x02\x06\x20"

codes = {
    "\\xf0@":"\n",
    "\\xf0G":"[G]",
    "\\xf0D":"[D]",
    "\\xf0H": "[HEAD]",
    }

def intlit(byte):
    return int.from_bytes(byte, byteorder="little")

def extract_msb(filename):
    file = open(Path(f"DVDDATA/adv/msb/{filename}.msb").resolve(), "rb")
    header = file.read(8)
    assert header == MSB_MAGIC, "Invalid header file!"
    print(header)

    csvfile = open(f"csv\\{filename}.csv", "w", newline="", encoding="utf-8")
    writer = csv.writer(csvfile)

    writer.writerow(["Speaker", "JP Text", "EN Text", "Unknown", "Comments"])

    fileSize = intlit(file.read(4))
    strCount = intlit(file.read(4))

    strInfo = []

    for _ in range(strCount):
        num1 = intlit(file.read(4))     # Offset to Speaker
        num2 = intlit(file.read(4))     # Text Offset
        num3 = intlit(file.read(4))     # Unknown

        strInfo.append([num1, num2, num3])

    for i in range(strCount):
        file.seek(strInfo[i][1])
        data = bytearray()
        byte = intlit(file.read(1))
        while byte != 0x00:
            byte = (byte ^ 0xFF) + 1
            data.append(byte)
            byte = intlit(file.read(1))

        string = data.decode(encoding="shiftjis", errors="backslashreplace")

        if strInfo[i][0] == 0:
            speaker = "None"
        
        else:    
            file.seek(strInfo[i][0])
            data = bytearray()
            byte = intlit(file.read(1))
            while byte != 0x00:
                byte = (byte ^ 0xFF) + 1
                data.append(byte)
                byte = intlit(file.read(1))
        
            speaker = data.decode(encoding="shiftjis", errors="backslashreplace")
        

        for code, newcode in codes.items():
            string = string.replace(code, newcode)


        writer.writerow([speaker, string, "", f"{strInfo[i][2]}", ""])


def extract_text():

    for msb in MSB_FILES:
        extract_msb(msb)