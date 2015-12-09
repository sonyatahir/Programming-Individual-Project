# -*- coding: utf-8 -*-

import pandas as pd
from pandas.io import wb
import MySQLdb as myDB
import numpy as np



def GetData():

    
    #Children out of school, primary, male
    indm = "SE.PRM.UNER.MA"
    m = wb.download(indicator=indm, country="all", start = 2000, end =2015)
    m = m[544:]
    
    #Children out of school, primary, female
    indf = "SE.PRM.UNER.FE"
    f = wb.download(indicator=indf, country="all", start = 2000, end =2015)
    f = f[544:]
    
      
    f.reset_index(inplace=True) 
    m.reset_index(inplace=True) 
    
    fAvg = f.groupby('country').agg({'SE.PRM.UNER.FE': np.mean})
    mAvg = m.groupby('country').agg({'SE.PRM.UNER.MA': np.mean})
    
    fAvg = fAvg.fillna(0)
    mAvg = mAvg.fillna(0)
    
    fAvg.reset_index(inplace=True) 
    mAvg.reset_index(inplace=True)
    
    return f, m, fAvg, mAvg
    
def CreateDatabase():
    
    
    conn = myDB.connect('localhost', 'mysqluser', 'mysqlpass')
    cursor = conn.cursor()
    
    sql = 'DROP DATABASE IF EXISTS School;'
    cursor.execute(sql)   
    
    sql = 'CREATE DATABASE School;'
    cursor.execute(sql)
    sql = 'USE School;'
    cursor.execute(sql)
    qry = 'SET autocommit=1;'
    cursor.execute(qry)
    
    
    sql = '''CREATE TABLE OUTOFSCHOOL (
            Country varchar(50),
            Year varchar(4),
            Gender varchar(6),
            Count float);'''
    cursor.execute(sql)
    
    #Inserting data into the table
    for i in range (0,len(fStats)):
        country = fStats.iloc[i][0]
        year = fStats.iloc[i][1]

        if pd.isnull(fStats.iloc[i][2]):
            count = float(fAvg[fAvg['country'] == country]['SE.PRM.UNER.FE'])
        else:
            count = float(fStats.iloc[i][2])

            
        sql = 'INSERT INTO OUTOFSCHOOL VALUES ("{}","{}","FEMALE",{});'.format(country,year,count)
        cursor.execute(sql)
      
    for i in range (0,len(mStats)):
        country = mStats.iloc[i][0]
        year = mStats.iloc[i][1]

        if pd.isnull(mStats.iloc[i][2]):
            count = float(mAvg[mAvg['country'] == country]['SE.PRM.UNER.MA'])
        else:
            count = float(mStats.iloc[i][2])

            
        sql = 'INSERT INTO OUTOFSCHOOL VALUES ("{}","{}","MALE",{});'.format(country,year,count)
        cursor.execute(sql)
        
    
    cursor.close()
    
def CreateCSV():
    
    conn = myDB.connect('localhost', 'mysqluser', 'mysqlpass')
    cursor = conn.cursor()
    
    sql = 'USE School;'
    cursor.execute(sql)
    
    sql = 'SELECT * from OUTOFSCHOOL where Gender = "MALE"'
    male = pd.read_sql(sql, conn)

    sql = 'SELECT * from OUTOFSCHOOL where Gender = "FEMALE"'
    female = pd.read_sql(sql, conn)
     
    male.to_csv('male.csv')
    female.to_csv('female.csv')
    
    cursor.close()

def AnalyzeTotal():
    conn = myDB.connect('localhost', 'mysqluser', 'mysqlpass')
    cursor = conn.cursor()
    
    sql = 'USE School;'
    cursor.execute(sql)
    
    sql = '''SELECT Year, sum(Count) as Count from OUTOFSCHOOL 
    where Gender = "MALE"
    group by Year
    order by Year;'''
    cursor.execute(sql)
    mTotal = []
    yearLabels = []
    for c in cursor:
        yearLabels.append(c[0])
        mTotal.append(c[1])
        
    sql = '''SELECT Year, sum(Count) as Count from OUTOFSCHOOL 
    where Gender = "FEMALE"
    group by Year
    order by Year;'''
    cursor.execute(sql)
    fTotal = []
    for c in cursor:
        fTotal.append(c[1])
    
    cursor.close()
    
    PlotBarChart(yearLabels,mTotal,fTotal)

def AnalyzeTop15Countries():
    conn = myDB.connect('localhost', 'mysqluser', 'mysqlpass')
    cursor = conn.cursor()
    
    sql = 'USE School;'
    cursor.execute(sql)
    
    sql = '''select a.Country, maleCounts, femaleCounts, maleCounts+femaleCounts as totalCounts
            FROM
            (
                (SELECT Country, sum(Count) as maleCounts
                FROM OUTOFSCHOOL
                where Gender = "MALE"
                GROUP BY Country ) a
            
                join
            
                (SELECT Country, sum(Count) as femaleCounts
                FROM OUTOFSCHOOL
                where Gender = "FEMALE"
                GROUP BY Country ) b
            
                on a.Country = b.Country
            )
            order by totalCounts desc
            LIMIT 15;'''
    
    cursor.execute(sql)
    maleCounts = []
    femaleCounts = []
    countryLabels = []
    for c in cursor:
        countryLabels.append(c[0])
        maleCounts.append(c[1])
        femaleCounts.append(c[2])
        
    
    cursor.close()
    
    PlotBarChart(countryLabels,maleCounts,femaleCounts)

    
def PlotBarChart(xlabels, group1, group2):
    import matplotlib.pyplot as plt
    import numpy as np
    import textwrap
    

    N = len(xlabels)
    ind = np.arange(N)
    w = 0.30
    
    x = group1
    y = group2
    labels=[textwrap.fill(text,15) for text in xlabels]
    
    fig, ax = plt.subplots(figsize=(10,5))
    rects1 = ax.bar(ind, x, w, color='r')    
    rects2 = ax.bar(ind + w, y, w, color='y')

    ax.set_ylabel('Count')
    ax.set_title('Count of Children Out of School')
    ax.set_xticks(ind + w)
    ax.set_xticklabels(labels)
    

    ax.legend((rects1[0], rects2[0]), ('Male', 'Female'))
    

    plt.show() 
    
    
fStats, mStats, fAvg, mAvg = GetData()
CreateDatabase()
CreateCSV()
AnalyzeTotal()
AnalyzeTop15Countries()







