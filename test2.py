import sys

with open(sys.argv[1]) as file0:    # opens the text file given to the program
    lines=file0.readlines()         # makes a list of all the lines in the file

words=lines[339].split('>')         # makes a list of the elements separated by '>' in the 340th line of the file

if(words[-4:-1]==['<span','Donation Received</span','</p']):    # checks if the text file contains is an email related to donation
    details=lines[348].split('>')[2].split()                    # makes a list of strings containing donation details
    n=len(details)

    print("\nNew details:-")
    print("Contributor email: "+(details[-1])[1:len(details[-1])-8])    # filtering details for storage
    for i in range(n):
        if(details[i]=='from'):
            break
    print("Amount: "+details[i-2])
    print("Currency: "+details[i-1])
    print("Contributor: ",end='')
    for j in range(i,n):
        if(i!=n-2):
            i+=1
            print(details[i]+" ",end='')
    for i in range(40):
        if(lines[i].split()[0]=='Date:'):
            break
    print('\n'+(lines[i]),end='')
