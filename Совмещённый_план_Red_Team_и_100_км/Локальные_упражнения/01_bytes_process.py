"""Unicode, bytes, hash, PID. Standard library only."""
import hashlib
import os

text = "Привет"
data = text.encode("utf-8")
changed = bytearray(data)
changed[-1] ^= 1
print("PID:", os.getpid())
print("Unicode characters:", len(text))
print("UTF-8 bytes:", len(data))
print("Bytes:", data.hex(" "))
print("Round trip:", data.decode("utf-8") == text)
print("SHA256 original:", hashlib.sha256(data).hexdigest())
print("SHA256 changed: ", hashlib.sha256(changed).hexdigest())
print("A hash alone does not authenticate the sender.")
