# mini voting system
vote1=0
vote2=0
vote3=0
vote4=0
def voting_system(age):
    candidates=["aman","Manjil","adi","rudra"]
    global vote1,vote2,vote3,vote4
     
    choose=input("enter the candidate you want to vote for (aman/manjil/adi/rudra): ").lower()
    if age>=18:
        if choose=="aman":
            vote1+=1
            return "you voted for aman"
        elif choose=="manjil":
            vote2+=1
            return "you voted for manjil"
        elif choose=="adi":
            vote3+=1
            return "you voted for adi"
        elif choose=="rudra":
            vote4+=1
            return "you voted for rudra"
        else:
            return "invalid candidate"
    else:
        return "you are not eligible to vote"
age=int(input("enter your age:"))
print(voting_system(age))
print("vote count for aman:",vote1)
print("vote count for manjil:",vote2)
print("vote count for adi:",vote3)
print("vote count for rudra:",vote4)