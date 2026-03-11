#atm pin validator
def validate_atm_pin(pin):
    attempts=3
    print("Welcome to ATM PIN validator")
    while attempts>0:
        user_pin=input("please enter your 4 digit ATM pin:")
        if user_pin==pin:
            return "PIN validated successfully!"
        else:
            attempts-=1
            print("incorrect PIN, you have",attempts,"attempts left")
    return "Too many incorrect attempts. account is blocked."
pin="1234"
print(validate_atm_pin(pin))