#password strength checker using python 
def check_password_strength(password):
    if len(password)<6:
        return "It is a weak password try a strong one"
     
    elif (len(password)>=6 and len(password)<=10) and (password.isalpha() or password.islower() or password.isupper() or password.isdigit() or password.special()):
        return "It is a medium password try a strong one"
    elif len(password)>10 and any(char.isupper() for char in password) and any(char.islower() for char in password) and any(char.isdigit() for char in password) and any(not char.isalnum() for char in password):
        return "It is a strong password"
    else:
        return "It is a medium password try a strong one"
password = input("Enter your password: ")
print(check_password_strength(password))


