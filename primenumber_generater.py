#prime number generator
def is_prime(num):
    count=0
    if num<2:
        return num,"is not a prime number"
    for i in range(2,num):
        if num%i==0:
            count+=1
            break
    if count==0:
        return num,"is a prime number"
    else:
        return num,"is not a prime number"
def generate_primes(limit):
    primes=[]
    for num in range(2,limit+1):
        if is_prime(num)[1]=="is a prime number":
            primes.append(num)
    return primes
limit=int(input("Enter the limit to generate prime numbers:"))
print("Prime numbers up to",limit,":",generate_primes(limit))