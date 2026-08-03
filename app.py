def cryptoclub_ch01(message):
    plaintext = "abcdefghijklmnopqrstuvwxyz"
    ciphertext = "DEFGHIJKLMNOPQRSTUVWXYZABC"
    
    encrypted_message = []
    
    for char in message:
        if char in plaintext:
            number = plaintext.index(char)

            encrypted_message.append(ciphertext[number])
        else:
            encrypted_message.append(char)
            
    return "".join(encrypted_message)
