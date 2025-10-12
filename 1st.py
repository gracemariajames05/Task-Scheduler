a=int(input("Enter the first no:"))
b=int(input("Enter the second no:"))
for num in range(a,b+1):
    if num>1:
        for j in range(2,num):
            if (num%j)==0:
                break
        else:
            print(num)