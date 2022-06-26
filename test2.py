import sys
with open(sys.argv[1]) as file0:
    lines=file0.readlines()
words=lines[339].split('>')
if(words[-4:-1]==['<span','Donation Received</span','</p']):
    details=lines[348].split('>')[2].split()
    n=len(details)
    print("\nNew details:-")
    print("Contributor email: "+(details[-1])[1:len(details[-1])-8])
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
