import sys, csv

def _intlit(byte):
    return int.from_bytes(byte, byteorder="little")

MSB_MAGIC = b"MSB!"

codes = {
    "\\xf0@":"\n",
    "\\xf0G":"[G]",
    "\\xf0G":"[D]",
    "\\xf0H": "[HEAD]",
    }

outname = sys.argv[1]

file = open(f"DVDDATA\\{outname}.bin", "rb")
header = file.read(4)
if header == MSB_MAGIC:
    print(header)
else:
    exit(f"Header {header} does not match MSB!")

out = open(f"out\\{outname}.txt", "w", encoding="utf-8")
csvfile = open(f"out\\{outname}.csv", "w", newline="", encoding="utf-8")
writer = csv.writer(csvfile)

writer.writerow(["Speaker", "JP Text", "EN Text", "Unknown", "Comments"])

print(file.read(4))
filesize = _intlit(file.read(4))
filecount = _intlit(file.read(4))

fileinfo = []

for _ in range(filecount):
    num1 = _intlit(file.read(4))
    num2 = _intlit(file.read(4))
    num3 = _intlit(file.read(4))

    fileinfo.append([num1, num2, num3])

for i in range(filecount):
    file.seek(fileinfo[i][1])
    data = bytearray()
    byte = _intlit(file.read(1))
    while byte != 0x00:
        byte = (byte ^ 0xFF) + 1
        data.append(byte)
        byte = _intlit(file.read(1))

    string = data.decode(encoding="shiftjis", errors="backslashreplace")

    if fileinfo[i][0] == 0:
        speaker = "None"
    
    else:    
        file.seek(fileinfo[i][0])
        data = bytearray()
        byte = _intlit(file.read(1))
        while byte != 0x00:
            byte = (byte ^ 0xFF) + 1
            data.append(byte)
            byte = _intlit(file.read(1))
    
        speaker = data.decode(encoding="shiftjis", errors="backslashreplace")
    
    out.write(f"speaker: {speaker} ({fileinfo[i][0]:X})\toffset: {fileinfo[i][1]:X}\tunknown1: {fileinfo[i][2]:X} ({fileinfo[i][2]})\n")

    for code, newcode in codes.items():
        string = string.replace(code, newcode)

    out.write(f"{string}\n\n")
    writer.writerow([speaker, string, "", f"{fileinfo[i][2]}", ""])
