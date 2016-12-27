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

def connect(item):  
    a = item.split(' ')
    b = a[0]
    for i in range(1,len(a)):
        b = b+'( )*(\n)*( )*'+a[i].lower()
    return b 
def connect2(itemlist):
    if not isinstance(itemlist,list):
        return connect(itemlist)
    else:
        a = '('+connect(itemlist[0])+')'
        for j in range(1,len(itemlist)):
            a = a+'|('+connect(itemlist[j])+')'
        return a   
def findall(k,pattern,text):
    pos = []
    a = re.search(pattern,text,re.S)
    b = 0
    if a:
        while a:
            pos.append((k,b+a.start(),b+a.end()))
            b = a.end()+b
            a = re.search(pattern,text[b:len(text)],re.S)
    return pos
def findnextno(listofnumbers):
    pairlist = []
    if len(listofnumbers)==0:
        return pairlist   
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
def findna(text):
    a = re.search('\\bn/a\\b',text)
    if a:
        return 'n/a'
    else:
        return ''
def findnumber(text):
    a = re.search('[1-9](?:\d{0,2})(?:,\d{3})*(?:\.\d*[1-9])?|0?\.\d*[1-9]|0',text)
    if a:
        return text[a.start():a.end()]
    else:
        return findna(text)
def findpercent(text):
    a = re.search('((100(\.(0)*)?)|([0-9]?[0-9](\.[0-9]*)?)|(0*\.[0-9]*))[%]',text)
    if a:
        return a.group()
    else:
        return findnumber(text)
def stripex(text,listex):
    for i in range(len(listex)):
        text = re.sub(listex[i],'',text)
    return text 
def emptyno(infolist):
    a = len(infolist)
    for i in range(len(infolist)):
        if isinstance(infolist[i],list):
            if len(infolist[i])>0:
                a-=1
        else:
            if infolist[i]!='':
                a-=1
    return a

info_collude = [] 
info_except = []   
# -- variables --
sep1 = '\n--------------------------------------'
sep2 = '--------------------------------------\n\n'
i1 = []
i1.append('name\(?s?\)? of (reporting|report) person\(?s?\)?:?')
i1.append('names? of filers\. i\.r\.s\. identification nos?\. of above persons? \(entities only\):?') # 1129
i1.append('names? and i\.r\.s\. identification nos?\. \(entities only\) of reporting persons?:?')
i2 = []
i2.append('check the (appropriate)? box if a? member of a? group:?')
i2.append('2\.( )check the appropriate? box if') # 59
i2.append('\(2\) check the appropriate box if a member')
i2.append('2 check the appropriate box if a member')
i3 = 'sec use only'
i4 = 'source of funds'
i5 = []
i5.append('check (box)? if disclosure of legal proceedings is required pursuant to items 2\(d\) or 2\(e\)')
i5.append('check (box)? if disclosure of legal proceedings is') # 59
i6 = 'citizenship or place of organization:?'
i7 = []
i7.append('sole voting power')
i7.append('sole dispositive power') # 59
i8 = 'shared voting power'
i9 = 'sole dispositive power'
i10 = 'shared dispositive power'
i11 = []
i11.append('aggregate amount beneficially owned by each (reporting)? person')
i12 = 'check box if (the)? aggregate amount in row \(11\) excludes certain shares'
i13 = 'percent of class represented by amount in row (\(11\))?'
i14 = []
i14.append('type of reporting person')
i14.append('type of person reporting') # 59
i4_c = ['sc','bk','af','wc','pf','oo']
i14_c = ['bd','bk','ic','iv','ia','ep','hc','sa','cp','co','pn','in','oo']
infos = [i1,i2,i3,i4,i5,i6,i7,i8,i9,i10,i11,i12,i13,i14]
for i in range(len(infos)):
    infos[i] = connect2(infos[i])
    #infos[i] = '('+str(i+1)+'|'+str(i+1)+'\.|\('+str(i+1)+'\))?( )*(\n)*( )*'+infos[i]
        
for i in range(len(collude_13)):
    # no infos: 271,2729,2818,3082,4653,5804
    if i%1000==0:
        print(i)
    cik = collude_13[i][0]
    fik = collude_13[i][1]
    folder_13 = folder+"\\text\\"
    folder_13_new = folder+"infos - collude\\"
    fname = folder_13+cik+"_"+fik+".txt"    
    fname_new = folder_13_new+cik+"_"+fik+".txt"
    f = open(fname,'r')
    doc = f.read().lower()
    f.close()
    # find places
    pos = []
    for j in range(len(infos)):
        a = findall(j,infos[j],doc)
        for k in range(len(a)):
            pos.append(a[k])
    pos = sorted(pos,key=itemgetter(1,0))
    pos_list = []
    pos_start = []
    selects = []
    for k in range(len(pos)):
        pos_list.append(pos[k][1])
        pos_start.append(pos[k][2])
    pos_end = findnextno(pos_list)
    try:
        for k in range(len(pos)):
            if pos[k][0]==0:
                selects.append(['']*len(infos))
                selects[len(selects)-1].append(cik)
                selects[len(selects)-1].append(fik)
                selects[len(selects)-1][0]=doc[pos_start[k]:pos_end[k]]
            elif pos[k][0]==13:
                selects[len(selects)-1][13]=doc[pos_start[k]:pos_start[k]+50]
            else:
                selects[len(selects)-1][int(pos[k][0])]=doc[pos_start[k]:pos_end[k]]
    except:
        info_except.append(i)
        continue
    precise = []
    for j in range(len(selects)):
        # (1) 
        if1 = selects[j][0].strip()
        # (2)
        a = selects[j][1].find('a')
        b = selects[j][1].find('b')
        x = selects[j][1].find('x')
        if x>a and x<b:
            if2_a = 'x'
            x = selects[j][1].find('x',b)
            if x>0:
                if2_b = 'x'
            else:
                if2_b = ''
        else:
            if2_a = ''
            if x>b:
                if2_b = 'x'
            else:
                if2_b = ''
        if2 = [if2_a,if2_b]        
        # (4)
        if4 = ['']*len(i4_c)
        for m in range(len(i4_c)):
            if re.search('\\b'+i4_c[m]+'\\b',selects[j][3],re.S):
                if4[m]='x'    
        # (5)
        if selects[j][4].find('x')>0:
            if5 = 'x'
        else:
            if5 = ''  
        # (6)
        if6 = selects[j][5].strip()
        # (7-11)
        if7 = findnumber(selects[j][6])
        if8 = findnumber(selects[j][7])
        if9 = findnumber(selects[j][8])
        if10 = findnumber(selects[j][9])
        if11 = findnumber(selects[j][10])
        # (12)
        if selects[j][11].find('x')>0:
            if12 = 'x'
        else:
            if12 = ''
        # (13)
        if13 = findpercent(selects[j][12])
        # (14)
        selects[j][13]=re.sub('instruction','',selects[j][13],flags=re.I)
        if14 = ['']*len(i14_c)
        for m in range(len(i14_c)):
            if re.search('\\b'+i14_c[m]+'\\b',selects[j][13],re.S):
                if14[m]='x'
        precise.append([if1, if2, if4, if5, if6, if7, if8, if9, if10, if11, if12, if13, if14, cik, fik])
    '''
    if len(precise)==0:
        precise.append(['',[],[],'','','','','','','','','',[],cik,fik])
    '''
    # write into file
    for j in range(len(precise)):
        if emptyno(precise[j])<8:
            info_collude.append(precise[j])
         
# ------------------------------ clean the cells -------------------------------

# -- excludes --
x1 = []
x1.append(connect('s(\.)?s(\.)? or i(\.)?r(\.)?s(\.)? identification nos?(\.)? of above persons?:?\.?'))
x1.append(connect('i(\.)?r(\.)?s(\.)? identification nos?(\.)? of above persons?:?\.?'))
x1.append('\\birs\\b|\\bidentification\\b|\\bno\\b|\\bein\\b|\\bnumber\\b|\\bid\\b|\\bna\\b')
x1.append('social security number:')
x1.append('not applicable')
x1.append('not required')
x1.append('intentionally omitted')
x1.append('\(?entities only\)?')
x1.append(connect('i r s nos of above persons'))
x1.append(connect('or of above person optional'))
x1.append(connect('ss or of above person'))
x1.append(connect('(or)? nos of above persons?'))
x1.append(connect('or of person'))
x1.append('[0-9]{5,10}')
x1.append('\\b\(?[1-9]|1[0-4]\)?\\b')
x1.append('\\b\(?2\)?\\b')
x1.append('\\b\(?3\)?\\b')
x1.append('\\btax\\b')
x1.append('\\bss\\b')
x1.append('^(and its)')
x1.append('^s|:|\.|/|\,|\(|\)|;')
x1.append('\(|\,$')
x1.append('#*')
x1.append('\|')
x2 = []
x2.append('check (the)? (appropriate)? box')
x2.append('check the appropriate')
x6 = []
x6.append('\\b\(?[1-9]\)?\.?\\b')
x6.append('\\bnumber\\b')
x6.append(':|\||\(|\)')
x7_11 = []
for j in range(5,14):
    x7_11.append(str(j))
for i in range(len(info_collude)):
    # info 2
    ref = info_collude[i][0]
    k = re.search(connect2(x2),ref,re.S)
    if k:
        info_collude[i][0] = info_collude[i][0][0:k.start()]
        a = ref.find('a')
        b = ref.find('b')
        x = ref.find('x')
        if x>a and x<b:
            if2_a = 'x'
            x = ref.find('x',b)
            if x>0:
                if2_b = 'x'
            else:
                if2_b = ''
        else:
            if2_a = ''
            if x>b:
                if2_b = 'x'
            else:
                if2_b = ''
        if2 = [if2_a,if2_b]
        info_collude[i][1] = if2
    # info 1
    info_collude[i][0] = stripex(stripex(info_collude[i][0],x1).strip(),x1) 
    info_collude[i][0] = re.sub('(\n)+',',',info_collude[i][0])
    info_collude[i][0] = re.sub('( )+',' ',info_collude[i][0]) 
    info_collude[i][0] = info_collude[i][0].strip()
    # info 7-11
    for j in range(5,10):
        if info_collude[i][j] in x7_11:
            info_collude[i][j]=''
    ref = info_collude[i][4]
    k = re.search(connect('sole voting'),ref,re.S)
    if k:
        info_collude[i][4] = info_collude[i][4][0:k.start()]
        info_collude[i][5] = findnumber(ref[k.start():len(ref)])
    # info 6
    ref = info_collude[i][4]
    k = re.search(connect('number of'),ref,re.S)
    if k:
        info_collude[i][4] = info_collude[i][4][0:k.start()]
    info_collude[i][4] = stripex(stripex(info_collude[i][4],x6).strip(),x6) 
    info_collude[i][4] = re.sub('(\n)+',',',info_collude[i][4])
    info_collude[i][4] = re.sub('( )+',' ',info_collude[i][4])
    info_collude[i][4] = re.sub(',|\.','',info_collude[i][4]) 
    info_collude[i][4] = info_collude[i][4].strip()
    # info 13
    if info_collude[i][11] in x7_11:
        info_collude[i][11]=''
    

# -------------------------- write into excel file -----------------------------

book = xlwt.Workbook()

# 1. Precise Information
sheet1 = book.add_sheet("Sheet 1")
# first line
sheet1.write(0,0,"cik")
sheet1.write(0,1,"fik")
sheet1.write(0,2,"1. name and irs")
sheet1.write(0,3,"2. check member of group")
sheet1.write(1,3,"a")
sheet1.write(1,4,"b")
sheet1.write(0,5,"4. source of funds")
for j in range(5,5+len(i4_c)):
    sheet1.write(1,j,i4_c[j-5].lower())
sheet1.write(0,11,"5. check disclosure")
sheet1.write(0,12,"6. citizenship")
sheet1.write(0,13,"7. sole voting power")
sheet1.write(0,14,"8. shared voting power")
sheet1.write(0,15,"9. sole dispositive power")
sheet1.write(0,16,"10. shared dispositive power")
sheet1.write(0,17,"11. aggregate amount")
sheet1.write(0,18,"12. check exclusion")
sheet1.write(0,19,"13. percentage")
sheet1.write(0,20,"14. type of reporting person")
for j in range(20,20+len(i14_c)):
    sheet1.write(1,j,i14_c[j-20].lower())
# i-th line
for i in range(1,len(info_collude)):
    sheet1.write(i+1,0,info_collude[i-1][-2])
    sheet1.write(i+1,1,info_collude[i-1][-1])
    sheet1.write(i+1,2,info_collude[i-1][0])
    for k in range(3,12):
        sheet1.write(i+1,k+8,info_collude[i-1][k])
    if len(info_collude[i-1][1])>1:
        sheet1.write(i+1,3,info_collude[i-1][1][0])
        sheet1.write(i+1,4,info_collude[i-1][1][1])
        for j in range(5,5+len(i4_c)):
            sheet1.write(i+1,j,info_collude[i-1][2][j-5])
        for j in range(20,20+len(i14_c)):
            sheet1.write(i+1,j,info_collude[i-1][12][j-20])
sheet2 = book.add_sheet("Sheet 2")
sheet2.write(0,0,"Exceptions (need manual work)")
sheet2.write(1,0,"No")
sheet2.write(1,1,"cik")
sheet2.write(1,2,"fik")
for i in range(len(info_except)):
    t = collude_13[info_except[i]]
    sheet2.write(i+2,0,i)
    sheet2.write(i+2,1,t[0])
    sheet2.write(i+2,2,t[1])
book.save(folder+"info 1-14_collude.xls")

        
        