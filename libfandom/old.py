import os

head = open("DVDDATA.h", "rb")
out = open("out.txt", "w", encoding="utf8")
tail = open("DVDDATA.i", "rb")
out2 = open("out2.txt", "w", encoding="utf8")
outdir = "PAC1"

os.makedirs(f"{outdir}", exist_ok=True)

print(head.read(8))
b"ToF2DpHd"

i = 0
while True:
    info = head.read(4)
    if info == b":EOF":
        break
    info = int.from_bytes(info, byteorder="little")
    out.write(f"{i}\t{info}\t{info:X}\n")
    i = i + 1
print("luke")
exit()


fileInfo = []

print(tail.read(4))
print(tail.read(8))
fileCount = int.from_bytes(tail.read(4), byteorder="little")

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
    
    tail.seek(fileInfo[i][1])
    fileData = tail.read(fileInfo[i][2])
    file = open(f"{outdir}\\{fileInfo[i][0]}", "w+b")
    file.write(fileData)

print("tear")