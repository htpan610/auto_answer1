
def toTxt(users):
    with open ('result.txt','w') as q:
        for i in users:
            for key, value in i.items():
                q.write(key)
                q.write(':')
                q.write(str(value))
                q.write(' / ')
            q.write('\n')


