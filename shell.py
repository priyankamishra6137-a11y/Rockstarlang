# *************************************
# Using interpreter in a input and print
#**************************************

# Importing tha interpreter file so this can use that
import cal1

# Asking user the equation and and returning the value form interpretor
while True:
    text = input('Basic> ')
    result, error = cal1.run(text)
 
    # Defferencing between error and normall
    if error:
        print(error.as_string())
    else:
        print(result)
