import bcrypt

password = b"hola"

# salt = bcrypt.gensalt()
# with open("salt.txt", 'wb') as file:
#     file.write(salt)

salt = b""
with open("salt.txt", 'r') as file:
    salt = file.read().encode("utf-8")

print(password)
hashed = bcrypt.hashpw(password, salt)
print(hashed)