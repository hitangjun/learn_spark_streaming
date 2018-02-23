#encoding=UTF-8
import datetime
ISOTIMEFORMAT = '%Y-%m-%d %X'
from pymongo import MongoClient
conn = MongoClient("192.168.1.246",50001)
db = conn.lymdb
def dateDiffInSeconds(date1,date2):
     timedelta = date2 - date1
     return timedelta.days*24*3600 +timedelta.seconds
db.lymtable.drop()
date1 = datetime.datetime.now()
for i  in range(1,600000):
    db.lymtable.insert({"name":"ljai","id":i,"addr":"fuzhou"})
c = db.lymtable.find().count()
print("count is ",c)
date2 = datetime.datetime.now()
print(date1)
print(date2)
print("消耗：",dateDiffInSeconds(date1,date2),"seconds")
conn.close()