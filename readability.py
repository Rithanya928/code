from cs50 import get_string

text = get_string("text:")

letters = 0
space = 0
sentences = 0
for characters in text:
    if characters.isalpha():
        letters += 1
    elif characters == ' ':
        space += 1
    elif characters == '.' or characters == '!':
        sentences += 1
words = space+1

L = (letters/words)*100
S = (sentences/words)*100

grade = 0.588*L-0.296*S-15.8

if grade > 16:
    print("grade 16+")
elif grade < 1:
    print("before grade 1")
else:
    print(f"grade{round(grade)}")
