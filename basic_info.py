import boto
import boto.s3
from boto.s3.key import Key
from boto.s3.connection import S3Connection
from IPython.parallel import Client

rc = Client()
rc.ids
dv = rc[:]
conn = S3Connection('AKIAIIGJGMKU6NPJNWRA','3KjkgAxCvShCWgJZqftD7R+mqoPBd5Eexz33qnmA')

# ------------------------------------- s3 -------------------------------------
b = conn.get_bucket('emr-yl')
index_13D = []
i = 0
for key in b.list('input/','/'):
    print(i)
    index_13D.append(key.name.encode('utf-8'))
    i+=1
index_13D.pop(0)

# ---------------------------- global variables --------------------------------
'''
# scrape information
FDATE = "FILED AS OF DATE:"
CDATE = "DATE AS OF CHANGE:"
GROUP = "GROUP MEMBERS:"
SUBJECT = "SUBJECT COMPANY:"
FILED = "FILED BY:"
SC13DA = "SC 13D/A"
SC13D = "SC 13D"
NAME = "COMPANY CONFORMED NAME:"
CIK = "CENTRAL INDEX KEY:"
SIC = "STANDARD INDUSTRIAL CLASSIFICATION:"
IRS = "IRS NUMBER:"
STATEa = "STATE OF INCORPORATION:"
STATEb = "STATE:"
FORM = "FORM TYPE:"
SEC = "SEC FILE NUMBER:"
FILM = "FILM NUMBER:"
STRa = "STREET1:"
STRb = "STREET2:"
CITY = "CITY:"
ZIP1 = "ZIP:"
PHONE = "BUSINESS PHONE:"
info = [NAME,CIK,SIC,IRS,STATEa,STATEb,FORM,SEC,FILM,STRa,STRb,CITY,ZIP1,PHONE]
'''

# -------------------------- define main function ------------------------------
@dv.parallel(block=True)
def echo(key):
    
    # -- variables --
    # scrape information
    FDATE = "FILED AS OF DATE:"
    CDATE = "DATE AS OF CHANGE:"
    GROUP = "GROUP MEMBERS:"
    SUBJECT = "SUBJECT COMPANY:"
    FILED = "FILED BY:"
    SC13DA = "SC 13D/A"
    SC13D = "SC 13D"
    NAME = "COMPANY CONFORMED NAME:"
    CIK = "CENTRAL INDEX KEY:"
    SIC = "STANDARD INDUSTRIAL CLASSIFICATION:"
    IRS = "IRS NUMBER:"
    STATEa = "STATE OF INCORPORATION:"
    STATEb = "STATE:"
    FORM = "FORM TYPE:"
    SEC = "SEC FILE NUMBER:"
    FILM = "FILM NUMBER:"
    STRa = "STREET1:"
    STRb = "STREET2:"
    CITY = "CITY:"
    ZIP1 = "ZIP:"
    PHONE = "BUSINESS PHONE:"
    info = [NAME,CIK,SIC,IRS,STATEa,STATEb,FORM,SEC,FILM,STRa,STRb,CITY,ZIP1,PHONE]
    
    # -- import --
    import sys
    import csv
    import re
    import os
    import boto
    import boto.s3
    import xlwt
    from boto.s3.key import Key
    from IPython.parallel import Client
    from boto.s3.connection import S3Connection
       
    # -- functions --
    def unique(l):
        return reduce(lambda x, y: x if y in x else x + [y], l, [])

    def findlastline(string, stringlist):
        import re
        allstring = ''
        n = -1
        a = re.compile(string)
        for i in range(0,len(stringlist)):
            allstring = allstring+stringlist[i].strip("\n")+" "
            if a.search(allstring,n+1):
                n = i
                break
        return n
   
    def findallline(string, stringlist):
        import re
        allstring = ''
        n = -1
        m = -1
        listn = []
        a = re.compile(string)
        for i in range(0,len(stringlist)):
            allstring = allstring+stringlist[i].strip("\n")+" "
            if a.search(allstring,m+1):
                m = a.search(allstring,m+1).end()
                n = i
                listn.append(n)
        return listn
    
    def stripinfos(keyword, stringlist, indexes):
        listn = []
        for i in range(0,len(indexes)):
            string = stringlist[indexes[i]]
            listn.append(string[string.find(keyword)+len(keyword)+1:len(string)].strip())
        return listn
    
    def stripinfo(keyword, stringlist, index):
        if index==-1:
            return ''
        else:
            string = stringlist[index]
            return string[string.find(keyword)+len(keyword)+1:len(string)].strip()
    
    def separate(separator,matrix):
        listn = [[],[]]
        for i in range(0,len(matrix)):
            l1 = []
            l2 = []
            for j in range(0,len(matrix[i])):
                if matrix[i][j]<separator:
                    l1.append(matrix[i][j])
                else:
                    l2.append(matrix[i][j])
            listn[0].insert(i,l1)
            listn[1].insert(i,l2)
        return listn
    
   
    # -- connection --
    conn = S3Connection('AKIAIIGJGMKU6NPJNWRA','3KjkgAxCvShCWgJZqftD7R+mqoPBd5Eexz33qnmA')
    b = conn.get_bucket('emr-yl')
    
    ###-- each file --
    key = str(key)
    fname = key[len('input/'):len(key)] # change
    f = open(fname,'w')
    b.get_key(key).get_file(f)
    f.close()
    f = open(fname,'r')
    doc = f.readlines()

    # -- operation --
    # 1. overall information
    fdate = findlastline(FDATE,doc)
    cdate = findlastline(CDATE,doc)
    members_i = findallline(GROUP,doc)
    subject = findlastline(SUBJECT,doc)
    filed = findlastline(FILED,doc)
    both_info_i = ['']*len(info)
    for j in range(0,len(info)):
        both_info_i[j] = findallline(info[j],doc)
    # 2. classification into filed and subject
    separator = max(subject,filed)
    l = separate(separator,both_info_i)
    if filed<subject:
        filed = l[0]
        subject = l[1]
    else:
        subject = l[0]
        filed = l[1]
    fdate = stripinfo(FDATE,doc,fdate)
    cdate = stripinfo(CDATE,doc,cdate)
    members_i = stripinfos(GROUP,doc,members_i)
    for j in range(0,len(info)):
        if subject[j]!=[]:
            subject[j]=stripinfo(info[j],doc,subject[j][0])
        else:
            subject[j]=''
        if filed[j]!=[]:
            filed[j]=stripinfo(info[j],doc,filed[j][0])
        else:
            filed[j]=''
    # 3. add to masklist

    [cik,fik] = fname.split('_')
    fik = fik.split('.')[0]
    
    # -- return
    # cik, fik, fdate, cdate, members_i, subject, filed
    Returns = [cik,fik]

    return Returns
  
echo.map(index_13D)
