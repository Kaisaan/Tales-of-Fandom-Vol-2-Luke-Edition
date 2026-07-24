# /// script
# requires-python = ">=3.12"
# dependencies = [
# ]
# ///

from fileio import FileIO
from pathlib import Path
from dataclasses import dataclass
import sys

@dataclass
class FileInfo:
    offset: int
    length: int

def main() -> None:
    if len(sys.argv) < 2:
        print("Not enough args!")
        sys.exit(-1)

    header = Path(sys.argv[1])
    content = Path(sys.argv[2])
    out_dir = Path(sys.argv[3])

    with FileIO(header) as f:
        head = f.read(8)
        print(head)

        assert head == b"ToF2DpHd", "Invalid header file!"

        entry_count = f.read_uint32()
        bucket_offset = f.read_uint32()
        bucket_entries = f.read_uint32()
        string_offsets = f.read_uint32()
        string_blob_offset = f.read_uint32()
        info_offset = f.read_uint32()

        print(f"Entry count: {entry_count:08X}")
        print(f"Bucket entries off: {bucket_offset:08X}")
        print(f"Buckets: {bucket_entries:08X}")
        print(f"Names off: {string_offsets:08X}")
        print(f"Names strtab: {string_blob_offset:08X}")
        print(f"Info off: {info_offset:08X}")

        f.seek(info_offset)
        infos: list[FileInfo] = []
        for _ in range(entry_count):
            off = f.read_uint32()
            ln = f.read_uint32()
            infos.append(FileInfo(off, ln))

        str_offsets = f.read_struct(f"<{entry_count}I", string_offsets)
        names: list[str] = []
        for i in range(entry_count):
            off = string_blob_offset + str_offsets[i]
            name = read_string_xor(f, pos = off)
            names.append(name.replace("\\", "/"))

        # Confirm that the metadata is correct

        # First the hash buckets
        buckets_original: list[int] = f.read_struct("<256H", bucket_offset) # type: ignore
        buckets_rebuilt: list[int] = [0] * 256
        buckets_counts: list[int] = [0] * 256
        for name in names:
            buckets_counts[hash_name(name)] += 1
        
        running = 0
        for i, count in enumerate(buckets_counts):
            buckets_rebuilt[i] = running
            running += count

        i = 0
        for og, nw in zip(buckets_original, buckets_rebuilt):
            if og != nw:
                raise ValueError(f"Hash bucket list mismatch at index {i}! {og} vs {nw}")
            i += 1
        
        # Now the indices for the buckets
        indices_original: list[int] = f.read_struct(f"<{entry_count}H", bucket_entries) # type: ignore
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

        
    with FileIO(content) as f:
        for i, name in enumerate(names):
            offset = infos[i].offset
            length = infos[i].length
            
            # print(f"0x{offset:08X} 0x{length:08X}", name)
            
            p = out_dir / name
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(f.read_at(offset, length))

def read_string_xor(f: FileIO, encoding: str = "utf8", pos: int = -1) -> str:
    _pos = f.offset if pos < 0 else pos

    buf: list[int] = []

    i = 0
    while True:
        b = f.read_uint8(_pos + i) ^ 0x40
        if b == 0:
            break
        buf.append(b)
        i += 1

    raw = bytes(buf)

    return raw.decode(encoding)

def hash_name(name: str) -> int:
    name = name.lower().replace('/', '\\')
    return sum(name.encode('ascii')) & 0xFF


if __name__ == "__main__":
    main()