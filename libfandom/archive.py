import os

def intlit(b: bytes) -> int:
    return int.from_bytes(b, byteorder="little")

def _writeint(num, size):
    return num.to_bytes(size, byteorder="little")

TOF_MAGIC = b"ToF2DpHd"

def native_path(path: str) -> str:
    return path.replace("\\", os.sep)

def unpack(name: str):
    head = open(f"extracted/{name}.h", "rb")
    info = open(f"extracted/{name}.i", "rb")
    log = open(f"{name}.txt", "w", encoding="utf-8")
    out = f"{name}"
    os.makedirs(out, exist_ok=True)

    header = head.read(8)
    assert header == TOF_MAGIC, "Invalid header file!"

    entry_count = intlit(head.read(4))
    bucket_offset = intlit(head.read(4))
    bucket_entries = intlit(head.read(4))
    string_offsets = intlit(head.read(4))
    string_blob_offset = intlit(head.read(4))
    info_offset = intlit(head.read(4))

    print(f"Entry count: {entry_count:08X}")
    print(f"Bucket entries off: {bucket_offset:08X}")
    print(f"Buckets: {bucket_entries:08X}")
    print(f"Names off: {string_offsets:08X}")
    print(f"Names strtab: {string_blob_offset:08X}")
    print(f"Info off: {info_offset:08X}")
    
    log.write(f"{entry_count:X} {bucket_offset:X} {bucket_entries:X} {string_offsets:X} {string_blob_offset:X} {info_offset:X}\n")

    head.seek(info_offset)

    fileInfo = []
    for x in range(entry_count):
        off = intlit(head.read(4))
        ln = intlit(head.read(4))
        fileInfo.append([off, ln])
    
    head.seek(string_offsets)

    str_offsets = []
    for x in range(entry_count):
        off = intlit(head.read(4))
        str_offsets.append(off)

    names = []
    for i in range(entry_count):
        offset = string_blob_offset + str_offsets[i]
        head.seek(offset)

        buffer = []
        while True:
            byte = intlit(head.read(1)) ^ 0x40

            if byte == 0:
                break
            else:
                buffer.append(byte)
            
        raw = bytes(buffer)

        string = raw.decode(encoding="utf-8")
        string = native_path(string)
        log.write(f"{string}\n")
        names.append(string)
    print(names)

    # Verify the hashes and the buckets
    
    head.seek(bucket_offset)

    buckets_original = []
    for i in range(256):
        val = intlit(head.read(2))
        buckets_original.append(val)

    buckets_counts: list[int] = [0] * 256
    for name in names:
        val = hash_name(name)
        buckets_counts[val] += 1

    buckets_rebuilt: list[int] = [0] * 256
    running = 0
    for i, count in enumerate(buckets_counts):
        buckets_rebuilt[i] = running
        running += count

    i = 0
    for og, nw in zip(buckets_original, buckets_rebuilt):
        if og != nw:
            raise ValueError(f"Hash bucket list mismatch at index {i}! {og} vs {nw}")
        i += 1

    # Verify the indices

    head.seek(bucket_entries)

    indices_original = []
    for i in range(entry_count):
        val = intlit(head.read(2))
        indices_original.append(val)

    indices_rebuilt: list[int] = [0] * entry_count

    next_pos = list(buckets_original)
    for index, name in enumerate(names):
        h = hash_name(name)
        indices_rebuilt[next_pos[h]] = index
        next_pos[h] += 1

    i = 0
    for og, nw in zip(indices_original, indices_rebuilt):
        if og != nw:
            raise ValueError(f"Hash index list mismatch at index {i}! {og} vs {nw}")
        i += 1

    for i, name in enumerate(names):
        print(name)
        name = native_path(name)
        offset = fileInfo[i][0]
        length = fileInfo[i][1]

        fileName = os.path.split(name)[1]
        fileDir = os.path.split(name)[0]

        os.makedirs(os.path.join(out, fileDir), exist_ok=True)

        info.seek(offset)
        fileData = info.read(length)

        newFile = open(os.path.join(out, fileDir, fileName), "wb")
        newFile.write(fileData)




def hash_name(name: str) -> int:
    return sum(name.encode('ascii')) & 0xFF


def main():
    unpack("DVDDATA")
    unpack("BGM")
    unpack("VOICE")
