#custom power function
def custom_power(base,exponent):
    result=1
    for _ in range(exponent):
        result*=base
    return result
base=int(input("enter the base of the power function: "))
exponent=int(input("enter the exponent of the power function: "))
print(custom_power(base,exponent))