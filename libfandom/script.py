import csv, os
from pathlib import Path

MSB_FILES = ["mlist_00topa", "mlist_01tosa", "mlist_02toaa", "mlist_03toab", "mlist_04tofa", "mlist_05tope", "mlist_06tetc"]
MSB_MAGIC = b"MSB!\x09\x02\x06\x20"

codes = {
    "\\xf0@": "\n",
    "\\xf0G": "[G]",
    "\\xf0D": "[D]",
    "\\xf0H": "[HEAD]",
    }

decodes = {
    b"\xf0@": b"\n",
    b"\xf0G": b"[G]",
    b"\xf0D": b"[D]",
    b"\xf0H": b"[HEAD]",
    }


def intlit(byte):
    return int.from_bytes(byte, byteorder="little")

def writeint(num: int, size: int=4):
    return num.to_bytes(size, byteorder="little")

def extract_msb(filename):
    file = open(Path(f"DVDDATA/adv/msb/{filename}.msb").resolve(), "rb")
    header = file.read(8)
    assert header == MSB_MAGIC, "Invalid header file!"

    csvfile = open(f"csv\\{filename}.csv", "w", newline="", encoding="utf-8")
    writer = csv.writer(csvfile)

    writer.writerow(["JP Speaker", "EN Speaker", "JP Text", "EN Text", "ID", "Comments"])

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
            if speaker.strip() == "":
                speaker = "Empty"
        

        for code, newcode in codes.items():
            string = string.replace(code, newcode)


        writer.writerow([f"{speaker}", "", f"{string}", "", f"{strInfo[i][2]}", ""])

    print(f"{filename} extracted!")


def extract_text():

    for msb in MSB_FILES:
        extract_msb(msb)

def make_msb(msb_file, csv_file):

    msb = open(f"{msb_file}.msb", "wb")

    speakers = []
    speakerInfo = {}
    lineCount = 0
    lineInfo = []
    with open(csv_file, "r", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        # Get unique speakers and linecount in first loop
        for row in reader:
            lineCount += 1
            if row["EN Speaker"] == "EN Speaker":
                continue

            if row["EN Speaker"] in speakers:
                continue

            if row["EN Speaker"] == "":
                if row["JP Speaker"] in speakers:
                    continue
                else:
                    speakers.append(row["JP Speaker"])

            else:
                print(lineCount)
                speakers.append(row["EN Speaker"])


        msb.write(MSB_MAGIC)
        msb.write(writeint(0))
        msb.write(writeint(lineCount))

        # Write dummy data to later calculate speaker offsets
        for i in range(lineCount):
            msb.write(writeint(0))
            msb.write(writeint(0))
            msb.write(writeint(0))

        padding = 16 - (msb.tell() % 16)
        if 16 > padding > 0:
            msb.write(bytes(padding))

        for speaker in speakers:
            if speaker == "None":
                continue
            offset = msb.tell()
            speakerInfo.update({speaker: offset})
            if speaker == "Empty":
                speaker == "  "
            speakerData = bytearray(speaker.encode("shift-jis", errors="backslashreplace"))

            encoded = bytearray()
            for byte in speakerData:
                byte = byte - 1
                byte = byte ^ 0xFF
                encoded.append(byte)

            msb.write(encoded)
            msb.write(bytes(1))

        padding = 16 - (msb.tell() % 16)
        if padding != 0:
            msb.write(bytes(padding))

        fp.seek(0)
        reader = csv.DictReader(fp)
        for row in reader:
            offset = msb.tell()

            if row["EN Text"] == "":
                text = row["JP Text"]
            else:
                text = row["EN Text"]

            textData = text.encode("shift-jis", errors="backslashreplace")

            for code, newcode in decodes.items():
                textData = textData.replace(newcode, code)

            textData = bytearray(textData)
            encoded = bytearray()
            for byte in textData:

                byte = byte - 1
                byte = byte ^ 0xFF
                encoded.append(byte)

            msb.write(encoded)
            msb.write(bytes(1))

            if row["EN Speaker"] == "":
                speaker = row["JP Speaker"]
            else:
                speaker = row["EN Speaker"]

            id = int(row["ID"])

            lineInfo.append([speaker, offset, id])


        padding = 16 - (msb.tell() % 16)
        if padding != 0:
            msb.write(bytes(padding))

        filesize = msb.tell()

        msb.seek(8)
        msb.write(writeint(filesize))
        msb.write(writeint(lineCount))

        for i in range(lineCount):
            speaker = lineInfo[i][0]
            if speaker == "None":
                speakeroffset = 0
            else:
                speakeroffset = int(speakerInfo[speaker])
            msb.write(writeint(speakeroffset))
            msb.write(writeint(lineInfo[i][1]))
            msb.write(writeint(lineInfo[i][2]))

def build_text():

    for msb in MSB_FILES:
        make_msb(msb)