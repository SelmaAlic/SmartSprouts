import bcrypt

def to_encrypt(password):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed.decode() #this will be stored in database

def verify_encryption(input_password, stored_hashed_password):
    return bcrypt.checkpw(input_password.encode(), stored_hashed_password.encode()) #checks raw password with password from database
