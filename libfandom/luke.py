import os, sys

name = sys.argv[1]

def _intlit(byte):
    return int.from_bytes(byte, byteorder="little")

head = open(f"{name}.h", "rb")
out = open(f"{name}.txt", "w", encoding="utf8")
tail = open(f"{name}.i", "rb")
os.makedirs(f"{name}", exist_ok=True)

TOF_MAGIC = b"ToF2DpHd"
PAC_MAGIC = b"PAC!"

if head.read(8) == TOF_MAGIC:
    print("luke")

fileCount = _intlit(head.read(4))
offset1 = _intlit(head.read(4))
offset2 = _intlit(head.read(4))
offset3 = _intlit(head.read(4))
offset4 = _intlit(head.read(4))
offset5 = _intlit(head.read(4))
print(f"{fileCount:X} {offset1:X} {offset2:X} {offset3:X} {offset4:X} {offset5:X} ")

head.seek(offset1)
for i in range((offset2 - offset1) // 4):
    start = _intlit(head.read(2))
    end = _intlit(head.read(2))
    out.write(f"{start:X}\t{end:X}\n")

out.write("luke1\n")

head.seek(offset2)
for i in range((fileCount // 2) + 1):
    start = _intlit(head.read(2))
    end = _intlit(head.read(2))
    diff = end - start
    out.write(f"{start:X}\t{end:X}\t{diff:X}\n")

out.write("luke2\n")

head.seek(offset3)
for i in range(fileCount):
    num = _intlit(head.read(4))
    out.write(f"{num:X}\n")

out.write("luke3\n")

head.seek(offset4)
for i in range((offset5 - offset4)):
    byte = head.read(1)
    info = _intlit(byte)
    print(byte)
    out.write(f"{info:X}\n")

out.write("luke4\n")

head.seek(offset5)
for i in range(fileCount):
    start = _intlit(head.read(4))
    size = _intlit(head.read(4))
    
    file = open(f"{name}\\file{i}.bin", "w+b")
    tail.seek(start)
    data = tail.read(size)
    file.write(data)

    file.seek(0)
    header = file.read(4)

    out.write(f"file{i}\t{header}\t{start:X}\t{size:X}\n")

    if header == PAC_MAGIC:
        os.makedirs(f"{name}\\file{i}", exist_ok=True)
        unknown1 = file.read(4)
        pacSize = file.read(4)
        pacCount = _intlit(file.read(4))
        fileInfo = []

        for _ in range(pacCount):

            fileName = file.read(32).decode(encoding="utf-8", errors="backslashreplace")
            fileName = fileName[:fileName.find("\x00")]

            if fileName == "":
                break

            fileOffset = _intlit(file.read(4))
            fileSize = _intlit(file.read(4))

            if (fileOffset == 0) and (fileSize == 0):
                break

            out.write(f"{fileName}\t{fileOffset:X}\t{fileSize:X}\n")

            fileInfo.append([fileName, fileOffset, fileSize])

        for j in range(pacCount):
            
            file.seek(fileInfo[j][1])
            fileData = file.read(fileInfo[j][2])
            newFile = open(f"{name}\\file{i}\\{fileInfo[j][0]}", "w+b")
            newFile.write(fileData)
    else:
        pass

    

    

print(head.read(4))


