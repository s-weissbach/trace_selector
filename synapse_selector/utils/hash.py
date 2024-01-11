from hashlib import sha256


def sha256_hash(filepath: str, buffersize: int = 65536) -> str:
    hasher = sha256()
    with open(filepath, "rb") as f:
        while True:
            data = f.read(buffersize)
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()
