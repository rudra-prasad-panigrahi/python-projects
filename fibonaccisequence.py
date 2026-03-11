#fibonacci sequency
def fibonacci_sequence(n):
    sequence=[]
    a,b=0,1
    for _ in range(n):
        sequence.append(a)
        a,b=b,a+b
    return sequence
num=int(input("enter the number of terms in the fibonacci sequence: "))
print("Fibonacci sequence:",fibonacci_sequence(num))