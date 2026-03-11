#grade calculator
def calculate_grade(marks):
    if marks>=90:
        return "you get ",'A',"grade"
    elif marks>=80:
        return "you get ",'B',"grade"
    elif marks>=70:
        return "you get ",'C',"grade"
    elif marks>=60:
        return "you get",'D',"grade"
    else:
        return "you get ",'F',"grade"
marks = float(input("Enter your marks: "))
print(calculate_grade(marks))