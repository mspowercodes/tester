import streamlit as st

def scramble_vowels(message):
    new_message = ""
    
    for char in message:
        if char == "a":
            new_message += "@"
        elif char == "e":
            new_message += "3"
        else:
            new_message += char
            
    return new_message

st.title("Vowel Scrambler")
user_text = st.text_input("Type a word:", value="apple")

if user_text:
    result = scramble_vowels(user_text)
    st.success(f"Scrambled: {result}")
