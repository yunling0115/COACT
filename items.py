import xlrd
import xlwt
import csv
import re
import os.path  
from operator import itemgetter, attrgetter
folder = "C:\\Users\\yling\\Jerchern\\"
collude_13 = []
with open(folder+"collude_screen_unique.csv","rb") as f:
    reader = csv.reader(f)
    for row in reader:
        collude_13.append(row)
collude_13.pop(0)
# 11754

def findnextno(listofnumbers):
    pairlist = []   
    for i in range(len(listofnumbers)):
        if listofnumbers[i]==0:
            pairlist.append(0)
            continue
        for j in range(i+1,len(listofnumbers)):
            if listofnumbers[j]>listofnumbers[i]:
                pairlist.append(listofnumbers[j])
                break
            if j==len(listofnumbers)-1:
                pairlist.append(listofnumbers[-1])
    pairlist.append(listofnumbers[-1])
    return pairlist 

def connect(item): 
    a = item.split(' ')
    b = a[0]
    for i in range(1,len(a)):
        b = b+'( )*(\n)*( )*'+a[i].lower()
    return b   

# -- variables --
sep1 = '\n------------------------------------- '
sep2 = ' -------------------------------------\n\n'
i1 = 'item 1 (\.)? security and issuer'
i2 = 'item 2 (\.)? identity and background'
i3 = 'item 3 (\.)? source and amount of funds or other consideration'
i4 = 'item 4 (\.)? purpose of transaction'
i5 = 'item 5 (\.)? interest in securities of the issuer'
i6 = 'item 6 (\.)? contracts(,)? arrangements(,)? understandings or relationships with respect to securities of the issuer'
i7 = 'item 7 (\.)? material to be filed as exhibits'
End = '\n( )*signature'
items = [i1,i2,i3,i4,i5,i6,i7]
for i in range(0,len(items)):
    items[i] = connect(items[i])
    
for i in range(len(collude_13)):
    if i%1000==0:
        print(i)
    cik = collude_13[i][0]
    fik = collude_13[i][1]
    folder_13 = folder+"\\text\\"
    folder_13_new = folder+"items - collude\\"
    fname = folder_13+cik+"_"+fik+".txt"    
    fname_new = folder_13_new+cik+"_"+fik+".txt"
    f = open(fname,'r')
    doc = f.read().lower()
    f.close()
    # find place
    pos = [0,0,0,0,0,0,0]
    for j in range(0,len(items)):
        if re.search(items[j],doc,re.S):
            pos[j] = re.search(items[j],doc,re.S).start()
    if re.search(End,doc,re.S):
        end = re.search(End,doc,re.S).start()
        if end<pos[-1]:
            end = doc.find(End,pos[-1])
    else:
        end = len(doc)
    ind = max(pos)
    pos.append(end)
    pos_end = findnextno(pos)    
    # write into list    
    g = open(fname_new,"w")
    g.write(cik+'_'+fik+'\n')
    for i in range(0,7):            
        g.write(sep1+str(i+1)+sep2+doc[pos[i]:pos_end[i]])
    g.close()     
    
        
     