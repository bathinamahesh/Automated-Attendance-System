s="Sam Harris"

def convert(string):
    a=list(string.split(" "))
    return a[0][0].upper()+"."+a[1][0].upper()

print(convert(s))
