import data

while True:
    text = input('>>>')
    result, error = data.run('<stdin>',text)

    if error: print(error.as_string())
    else: print(result)