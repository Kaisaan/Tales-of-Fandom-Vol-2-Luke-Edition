import os

tail = open("DVDDATA.i", "rb")
out2 = open("out2.txt", "w", encoding="utf8")
outdir = "PAC"

PAC_MAGIC = b"PAC!"



def extractPAC(offset, x):
    os.makedirs(f"{outdir}{x}", exist_ok=True)
    print(tail.read(8))


    fileCount = int.from_bytes(tail.read(4), byteorder="little")
    fileInfo = []

    for i in range(fileCount):

        fileName = tail.read(32).decode(encoding="utf-8", errors="backslashreplace")
        fileName = fileName[:fileName.find("\x00")]

        if fileName == "":
            break

        fileOffset = int.from_bytes(tail.read(4), byteorder="little")
        fileSize = int.from_bytes(tail.read(4), byteorder="little")

        if (fileOffset == 0) and (fileSize == 0):
            break

        out2.write(f"{fileName}\t{fileOffset:X}\t{fileSize:X}\n")

        fileInfo.append([fileName, fileOffset, fileSize])

    for i in range(fileCount):
        
        tail.seek(offset + fileInfo[i][1])
        fileData = tail.read(fileInfo[i][2])
        file = open(f"{outdir}{x}\\{fileInfo[i][0]}", "w+b")
        file.write(fileData)

    done = tail.tell()
    print(f"{done:X}")
    return done

def main():
    offset = 0
    x = 0
    while True:
        header = tail.read(4)
        if header != PAC_MAGIC:
            continue
        else:
            print(f"{offset:X}")
            newoffset = extractPAC(offset, x)
            offset = newoffset
            x = x + 1
            
    
if __name__ == "__main__":
    main()