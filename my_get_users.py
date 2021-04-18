import numpy as np
from xlrd import open_workbook

def get_users():
    book=open_workbook('user_names.xls')
    sheet=book.sheets()[0]
    users=[]
    for i in range(sheet.nrows):
        # print(sheet.row_values(i))
        user={'name':sheet.row_values(i)[1],'account':sheet.row_values(i)[2],'pw':sheet.row_values(i)[3]}
        users.append(user)
    users.pop(0)
    return users
    print(users)

# rows_num = table.nrows 获取行数
