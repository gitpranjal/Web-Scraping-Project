
# coding: utf-8

# In[2]:

import pandas as pd
import numpy as np
import urllib2
import urllib
from bs4 import BeautifulSoup
import requests
import unicodedata
pd.set_option('display.max_colwidth', -1)


# # Extracting all the Category links

# In[87]:


url = urllib.urlopen('https://www.findinall.com/')
content = url.read()
soup = BeautifulSoup(content, 'lxml')

table = soup.findAll('div',attrs={"class":"catlist-1 mt20"})
for div in table:
    links = div.findAll('a')
    for a in links:
        print a["title"]
        print  a['href']
        


# # Extracting info from each category link

# In[102]:

url = urllib.urlopen('https://www.findinall.com/shopping-category-768')
content = url.read()
soup = BeautifulSoup(content, 'lxml')

table = soup.findAll('div',attrs={"class":"pro-list-tb mt15"})
for x in table:
    print x.find("div").text
    print x.find("a")["href"]

# Another way to retrieve tables:
# table = soup.select('div[class="content-question"]')


# # Extracting all the information from all the categories

# In[3]:

link_list=[]
info_list=[]
category_list=[]
company_link=[]
contact_list=[]
contact_list=[]
page = requests.get("https://www.findinall.com/")
#url = urllib.urlopen('https://www.findinall.com/')
#content = url.read()
#soup = BeautifulSoup(content, 'lxml')
soup = BeautifulSoup(page.content, 'html.parser')

table = soup.findAll('div',attrs={"class":"catlist-1 mt20"})
for div in table:
    links = div.findAll('a')
    for a in links:
        print a["title"]
        print  a['href']
        link=a["href"]
        category=a["title"]
        #url = urllib.urlopen(str(link))
        #content = url.read()
        #category_soup = BeautifulSoup(content, 'lxml')
        category_page = requests.get(str(link))
        category_soup = BeautifulSoup(category_page.content, 'html.parser')
        contacts = category_soup.findAll('div',attrs={"class":"list-left ar fr"})
        table = category_soup.findAll('div',attrs={"class":"pro-list-tb mt15"})
        for x in table:
            print x.find("div").text
            info_list.append(x.find("div").text)
            category_list.append(category)
            organisation_link=x.find("a")["href"]
            print organisation_link
            company_link.append(organisation_link)
        for x in contacts:
            print x.text

            contact_link=x.find("a")["href"]
            print contact_link
            contact_page=requests.get(contact_link)
            contact_soup = BeautifulSoup(contact_page.content, 'html.parser')
            contact_info=contact_soup.find('div', attrs={"class":"w33 fl"})
            print contact_info.text
            contact_list.append(""+x.text.split("\n")[2]+" "+contact_link.strip()+" "+contact_info.text.strip())


# In[6]:

def remove_empty(lst):
    for element in lst:
        if len(element)==0:
            lst.remove(element)
        else:
            lst[lst.index(element)]=unicodedata.normalize('NFKD', element).encode('ascii','ignore')
            
        
    return lst


# # Parsing the information into DataFrame

# In[25]:

pd.set_option('display.max_colwidth', -1)
df=pd.DataFrame({"Category":category_list, "Company Info":info_list, "Company link":company_link, "Contacts":contact_list })
df["Company Info"]=df["Company Info"].apply(lambda info: info.split("\n"))
df["Company Info"]=df["Company Info"].apply(lambda lst: remove_empty(lst))


# In[26]:

name_list=[]
estabilished_list=[]
n_employees_list=[]
address_list=[]
state_list=[]
details_list=[]


# In[27]:

for lst in df["Company Info"]:
  
    name_list.append(lst[0])
    line=lst[1].split("/")
    try:
        year=int(line[0].split(":")[1].strip())
        estabilished_list.append(year)
    except:
        estabilished_list.append(np.nan)
        
    try:
        n_emp=int(line[1].split(":")[1].strip())
        n_employees_list.append(n_emp)
    except:
        n_employees_list.append(np.nan)
    
    try:
        add=lst[2].split(":")[1].strip()
        state=add[add.rindex(",")+1:].strip()
        address_list.append(add)
        state_list.append(state)
    except:
        address_list.append(lst[2].strip())
        state_list.append(np.nan)
        
    try:
        
        details=lst[3].split(":")[1].strip()
        details_list.append(details)
    except:
        details_list.append(np.nan)
   

    


# In[28]:


df["Company Name"]=name_list
df["Year of Estabilishment"]=estabilished_list
df["Number of employees"]=n_employees_list
df["Address"]=address_list
df["State"]=state_list
df["Details"]=details_list
df=df.drop("Company Info",  axis=1)


# In[29]:

df["Contacts"]=df["Contacts"].apply(lambda st: st.strip().split()[0]+" : "+st.strip().split()[-1])


# In[30]:

df.head()


# # Saving to file

# In[31]:

df.to_csv("Saletancy_Data.csv", index=False)


# In[32]:

from pandas import ExcelWriter


# In[33]:

writer = ExcelWriter('PythonExport.xlsx')
df.to_excel(writer,'Sheet5')
writer.save()

# DF TO CSV
df.to_csv('PythonExport.csv', sep=',')


# # Visual Data Analysis

# In[124]:

import seaborn as sns
import matplotlib.pyplot as plt
get_ipython().magic(u'matplotlib inline')
sns.set(rc={'figure.figsize':(11.7,8.27)})


# **Distribution of number of employees**
# Shows most of the companies have number of employees between 1 and 50

# In[126]:

sns.distplot(df[df["Number of employees"]<200]["Number of employees"])


# In[129]:

df[df["Number of employees"]<1000]["Number of employees"].hist()


# **Statewise distribution of numbet of companies**

# In[165]:

city=pd.DataFrame(df.groupby("State").count()["Company Name"])


# In[166]:

major_cities=city[city["Company Name"]>10]
major_cities["State"]=major_cities.index
major_cities["Number of companies"]=city["Company Name"]


# In[168]:

sns.set(rc={'figure.figsize':(21.7,12.27)})
sns.barplot(x="State", y="Company Name", data=major_cities)


# In[179]:

df.describe()


# **Correlation between Year of estabilshment and Number of employees**

# In[192]:

d=df[df["Year of Estabilishment"]>1970][df["Number of employees"]<1000]
df.corr()


# In[191]:

sns.lmplot(x="Year of Estabilishment", y="Number of employees", data=d)


# **Plot Showing top 10 employers**

# In[217]:

top_10_employers=df.sort_values(by="Number of employees", ascending=False).head(10)


# In[263]:

top_10_employers[["Company Name", "Number of employees"]]


# In[224]:

sns.set(rc={'figure.figsize':(21.7,12.27)})
plt.xticks(rotation=90)
sns.barplot(x="Company Name", y="Number of employees", data=top_10_employers)


# # Plot showing top 10 industries by employee size

# In[257]:

means=df.groupby("Category").describe()["Number of employees"]["mean"]
counts=df.groupby("Category").describe()["Number of employees"]["count"]
num_emp=means*counts


# In[258]:

num_emp=num_emp.sort_values(ascending=False).head(10)


# In[259]:

num_emp=pd.DataFrame(num_emp, columns=["Number of employees"])
num_emp


# In[260]:

sns.barplot(y=num_emp["Number of employees"], x=num_emp.index, data=num_emp)


# In[ ]:



