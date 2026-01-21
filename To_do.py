tasks=[]
while True:
    print("1. Add Task")
    print("2.View Tasks")
    print("3.Remove Task")
    print("4.Exit")

    choice=input("Enter your choice: ")
    if choice=='1':
        task=input("Enter the task: ")
        tasks.append(task)
        print("Task added successfully.")
    elif choice=='2':
        if len(tasks)==0:
            print("No tasks to show.")
        else:
            for i in range(len(tasks)):
                print(i+1,".",tasks[i])
    elif choice=='3':
        if len(tasks)==0:
            print("NO tasks to remove.")
        else:
            for i in range(len(tasks)):
                print(i+1,".",tasks[i])
                task_num=int(input("Enter the task number to remove: "))
                if 0<task_num<=len(tasks):
                    removed_task=tasks.pop(task_num-1)
                    print(f"Task '{removed_task}' removed successfully.")
                else:
                    print("Invalid task number.")
    elif choice=='4':
        print("Exiting the to-do list application.")
        break
    else:
        print("Invalid choice. Please try again.")