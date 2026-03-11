# banking system features deposite, withdrawal,balance check,transaction history,exit given user to only 3 attepts if faliled all block the user without oops concepts
def banking_system():
    balance=0
    transaction_history=[]
    attempts=3
    while attempts>0:
        print("1. Deposit")
        print("2. Withdraw")
        print("3. check balance")
        print("4. Transaction History")
        print("5. Exit")
        choice=int(input("enter your choice: "))
        if choice==1:
            amount=float(input("Enter amount to deposit:"))
            balance+=amount
            transaction_history.append("deposited: "+str(amount))
            print("Amount deposited successfully")
        elif choice==2:
            amount=float(input("Enter amount to Withdraw:"))
            if amount>balance:
                print("Insufficient balalnce")
                attempts-=1
                print("you have",attempts,"attempts left")
                if attempts==0:
                    print("Your account is blocked due to multiple failed attempts")
                    break
            else:
                balance-=amount
                transaction_history.append("withdrawn: "+str(amount))
                print("Amount withdraw sucessfully")
        elif choice==3:
            print("Your current balance is:",balance)
        elif choice==4:
            print("Transaction History:")
            for transaction in transaction_history:
                print(transaction)
        elif choice==5:
            print("Exiting the system. Thank you!")
            break        
        else:
            print("Invalid choice. Please try again.")
banking_system()

