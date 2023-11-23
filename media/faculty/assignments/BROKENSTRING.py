n=int(input())
for i in range(n):
    l=int(input())
    hf=int(l/2)
    part1=""
    part2=""
    st=input()
    part1=st[0:hf]
    part2=st[hf:l]
    if(part1+part2==part2+part1):
      print("YES")
    else:
      print("NO")



