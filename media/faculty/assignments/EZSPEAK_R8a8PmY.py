# cook your dish here
n=int(input())
for i in range(n):
    le=int(input())
    st=input()
    prev=-1
    curr=0
    for j in st:
        if(j =="a" or j=="e" or j=="i" or j=="o" or j=="u" or j =="A" or 
        j=="E" or j=="I" or j=="O" or j=="U"):
            prev=1
        else:
            prev=-1
        if(prev==-1):
        	curr+=1
        if(curr==4):
            break
        if(prev==1):
            curr=0;
    if(curr==4):
        print("NO")
    else:
        print("YES")