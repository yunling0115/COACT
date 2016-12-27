import sys
import boto
import boto.s3
from boto.s3.key import Key

from boto.s3.connection import S3Connection
conn = S3Connection('AKIAIIGJGMKU6NPJNWRA','3KjkgAxCvShCWgJZqftD7R+mqoPBd5Eexz33qnmA')

rs = conn.get_all_buckets()
b = conn.get_bucket('13d-yl')
f = open('index_13D.csv','w')
b.get_key('python programs/index_13D.csv').get_file(f)
f.close()
f = open('index_13DA.csv','w')
b.get_key('python programs/index_13DA.csv').get_file(f)
f.close()

import csv
index_13D = []
index_13DA = []
with open('index_13D.csv','rb') as f:
    reader = csv.reader(f)
    for row in reader:
        index_13D.append(row)
with open('index_13DA.csv','rb') as f:
    reader = csv.reader(f)
    for row in reader:
        index_13DA.append(row)
               
# split N each file ---------------------------------------------------------
N = 2000

index = index_13D.pop(0)
index_13DA.pop(0)

# 13D
matrix_13D = []
for i in range(len(index_13D)):
    if i%N==0:
        matrix_13D.append([])
        matrix_13D[len(matrix_13D)-1].append(index)
        matrix_13D[len(matrix_13D)-1].append(index_13D[i])
    else:
        matrix_13D[len(matrix_13D)-1].append(index_13D[i])
# 13DA
matrix_13DA = []
for i in range(len(index_13DA)):
    if i%N==0:
        matrix_13DA.append([])
        matrix_13DA[len(matrix_13DA)-1].append(index)
        matrix_13DA[len(matrix_13DA)-1].append(index_13DA[i])
    else:
        matrix_13DA[len(matrix_13DA)-1].append(index_13DA[i])
# write to csv file and upload
for i in range(len(matrix_13D)):
    with open(str(i)+'-13d.csv','wb') as f:
        writer = csv.writer(f)
        writer.writerows(matrix_13D[i])
for i in range(len(matrix_13DA)):
    with open(str(i)+'-13da.csv','wb') as f:
        writer = csv.writer(f)
        writer.writerows(matrix_13DA[i])
counter = 0
for i in range(len(matrix_13D)):
    fname = (str(i)+'-13d.csv').encode('utf-8')
    print fname
    k = b.new_key('python programs/parallel/'+str(counter)+'.csv')
    k.set_contents_from_filename(fname)
    counter+=1
for i in range(len(matrix_13DA)):
    fname = (str(i)+'-13da.csv').encode('utf-8')
    print fname
    k = b.new_key('python programs/parallel/'+str(counter)+'.csv')
    k.set_contents_from_filename(fname)
    counter+=1
    
# 13d: 45 csv
# 13da: 87 csv

# 13d: 89676 txt
# 13da: 172719 txt
'''
keys_13d = []
for key in b.list('13d/raw 13D/'):
    keys_13d.append(key.name.encode('utf-8'))
keys_13da = []
for key in b.list('13da/raw 13DA/'):
    keys_13da.append(key.name.encode('utf-8'))
    
for i in range(len(index_13D)):
    print(i)
    fname = 'H:\Jerchern1\\raw 13D\\'+index_13D[i][0]+'_'+index_13D[i][2]+'.txt'
    k = b.new_key('raw files/13D/'+index_13D[i][0]+'_'+index_13D[i][2]+'.txt')
    k.set_contents_from_filename(fname)
for i in range(len(index_13DA)):
    print(i)
    fname = 'H:\Jerchern1\\raw 13DA\\'+index_13DA[i][0]+'_'+index_13DA[i][2]+'.txt'
    k = b.new_key('raw files/13DA/'+index_13DA[i][0]+'_'+index_13DA[i][2]+'.txt')
    k.set_contents_from_filename(fname)   
'''            
        
