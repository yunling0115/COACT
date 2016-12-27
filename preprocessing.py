import sys
import csv
import re
import os
import boto
import boto.s3
from boto.s3.key import Key
import xlwt
from boto.s3.connection import S3Connection

def stripmultilines(data):
    p = re.compile('\n+')
    return p.sub('\n',data)
def stripxx(data):
    p = re.compile('-?_?\*?')
    data = p.sub('',data)
    p = re.compile('=*')
    return p.sub('',data)
def striphtml(data):
    p = re.compile('<.*?>')
    data = p.sub('',data)
    p = re.compile('<.*?\n.*?>')
    data = p.sub('',data)
    p = re.compile('<.*?\n.*?\n.*?>')
    data = p.sub('',data)
    p = re.compile('<.*?\n.*?\n.*?\n.*?>')
    data = p.sub('',data)
    p = re.compile('<.*?\n.*?\n.*?\n.*?\n.*?>')
    data = p.sub('',data)
    p = re.compile('<.*?\n.*?\n.*?\n.*?\n.*?\n.*?>')
    data = p.sub('',data)
    p = re.compile('<.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?>')
    data = p.sub('',data)
    p = re.compile('<.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?>')
    data = p.sub('',data)
    p = re.compile('<.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?>')
    data = p.sub('',data)
    p = re.compile('<.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?>')
    data = p.sub('',data)
    p = re.compile('<.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?\n.*?>')
    data = p.sub('',data)
    p = re.compile('=+')
    return p.sub('',data)
def stripspecial(data):
    p = re.compile(r'&.*?;')
    return p.sub('',data)

'''
# 13 D

index_13D = []
i = 0
for key in b.list('raw files/13D/','/'):
    print(i)
    index_13D.append(key.name.encode('utf-8'))
    i+=1
index_t13D = []
i = 0
for key in b.list('text files/13D/','/'):
    print(i)
    index_t13D.append(key.name.encode('utf-8'))
    i+=1
makeup = []
for i in range(len(index_13D)):
    print(i)
    fname = 'text files/13D/text-'+index_13D[i][14:len(index_13D[i])]
    if fname not in index_t13D:
        makeup.append(index_13D[i][14:len(index_13D[i])])

len(index_13D)-len(index_t13D)-len(makeup)

book = xlwt.Workbook(encoding="utf-8")
sheet1 = book.add_sheet("Sheet 1")
for i in range(len(makeup)):
    sheet1.write(i,0,makeup[i])
book.save("D:\\Dropbox\\AWS\\Jerchern\\index_13D_makeup.xls")

# 13 DA

index_13DA = []
i = 0
for key in b.list('raw files/13DA/','/'):
    print(i)
    index_13DA.append(key.name.encode('utf-8'))
    i+=1
index_t13DA = []
i = 0
for key in b.list('text files/13DA/','/'):
    print(i)
    index_t13DA.append(key.name.encode('utf-8'))
    i+=1
makeupA = []
index_13DA.pop(0)
for i in range(len(index_13DA)):
    print(i)
    fname = 'text files/13DA/text-'+index_13DA[i][15:len(index_13DA[i])]
    if fname not in index_t13DA:
        makeupA.append(index_13DA[i][14:len(index_13DA[i])])

len(index_13DA)-len(index_t13DA)-len(makeupA)

book = xlwt.Workbook(encoding="utf-8")
sheet1 = book.add_sheet("Sheet 1")
for i in range(len(makeupA)):
    sheet1.write(i,0,makeupA[i])
book.save("D:\\Dropbox\\AWS\\Jerchern\\index_13DA_makeup.xls")
'''

conn = S3Connection('AKIAIIGJGMKU6NPJNWRA','3KjkgAxCvShCWgJZqftD7R+mqoPBd5Eexz33qnmA')
rs = conn.get_all_buckets()
b = conn.get_bucket('13d-yl')
f = open('13D_index.csv','w')
b.get_key('python programs/index_13D_makeup.csv').get_file(f)
f.close()
f = open('13DA_index.csv','w')
b.get_key('python programs/index_13DA_makeup.csv').get_file(f)
f.close()

# 13D

index = []
with open('13D_index.csv','rb') as f:
    reader = csv.reader(f)
    for row in reader:
        index.append(row)
for i in range(1,len(index)):
    print(i)
    fname = index[i][0]
    key = 'raw files/13D/'+fname
    nkey = 'text files/13D/text-'+fname
    # Download to local --------------------------------------------------------
    #print key
    k = b.get_key(key)
    f = open(fname,'w')
    k.get_file(f)
    f.close()
    # preprocessing ------------------------------------------------------------    
    # (1) Exclude html tags (<*>) and special characters and separaters (==)
    f = open(fname,'r')
    g = open('text-'+fname, 'w')
    doc0 = f.read()
    f.close()
    doc0 = stripxx(striphtml(doc0))
    g.write(doc0)
    g.close()    
    # (2) Exclude html special characters (&...;)
    f = open('text-'+fname,'r')
    doc = f.readlines()
    f.close()
    g = open('text-'+fname,"w")
    new_doc = []
    for j in range(0,doc.__len__()):
        string = doc[j]
        string = stripspecial(string)
        if string.strip().__len__()>0:
            new_doc.append(string)
    g.writelines(new_doc)
    g.close()    
    # (3) Exclude mutliple lines
    f = open('text-'+fname,'r')
    doc0 = f.read()
    f.close()
    g = open('text-'+fname,"w")
    doc0 = stripmultilines(doc0)
    g.write(doc0)
    g.close()    
    # --------------------------------------------------------------------------  
    # upload to remote
    k = b.new_key(nkey)
    k.set_contents_from_filename('text-'+fname)
    
    
# 13DA

index = []
with open('13DA_index.csv','rb') as f:
    reader = csv.reader(f)
    for row in reader:
        index.append(row)
for i in range(1,len(index)):
    print(i)
    fname = index[i][0]
    key = 'raw files/13DA/'+fname
    nkey = 'text files/13DA/text-'+fname
    # Download to local --------------------------------------------------------
    #print key
    k = b.get_key(key)
    f = open(fname,'w')
    k.get_file(f)
    f.close()
    # preprocessing ------------------------------------------------------------    
    # (1) Exclude html tags (<*>) and special characters and separaters (==)
    f = open(fname,'r')
    g = open('text-'+fname, 'w')
    doc0 = f.read()
    f.close()
    doc0 = stripxx(striphtml(doc0))
    g.write(doc0)
    g.close()    
    # (2) Exclude html special characters (&...;)
    f = open('text-'+fname,'r')
    doc = f.readlines()
    f.close()
    g = open('text-'+fname,"w")
    new_doc = []
    for j in range(0,doc.__len__()):
        string = doc[j]
        string = stripspecial(string)
        if string.strip().__len__()>0:
            new_doc.append(string)
    g.writelines(new_doc)
    g.close()    
    # (3) Exclude mutliple lines
    f = open('text-'+fname,'r')
    doc0 = f.read()
    f.close()
    g = open('text-'+fname,"w")
    doc0 = stripmultilines(doc0)
    g.write(doc0)
    g.close()    
    # --------------------------------------------------------------------------  
    # upload to remote
    k = b.new_key(nkey)
    k.set_contents_from_filename('text-'+fname)