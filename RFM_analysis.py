#!/usr/bin/env python
# coding: utf-8

# # 데이터 불러오기

# In[1]:


import pandas as pd
import numpy as np


# In[2]:


# 이상치 처리 후 member와 sales 데이터를 합친 CSV 파일 읽어오기 
df = pd.read_csv("jeju_merge_sales_rm.csv" , encoding = 'utf-8')
df.head()


# In[3]:


# 문자열로 된 날짜를 Timestamp형식으로 변환
df['purchase_date'] = pd.to_datetime(df['purchase_date']) 


# In[4]:


# 사용할 칼럼만 추출 
df = df[['customer_id', 'purchase_id', 'purchase_date', 'purchase_amt']]


# In[5]:


df.head()


# # 데이터 변환

# In[6]:


base_date = pd.to_datetime('20191231') # 기준일: 2020-12-31
time_diff = df['purchase_date'] - base_date # 구매일과 기준일의 차이
df['purchase_date'] = abs(time_diff)
df['purchase_date'] = df['purchase_date'].astype('timedelta64[D]') # float형으로 변환 


# In[7]:


# Recency
recency_df = pd.DataFrame()
recency_df['Recency'] = df.groupby("customer_id")["purchase_date"].agg("min") # 최종 구매일과 기준일의 차이


# In[8]:


df_6m = df[df.purchase_date <= 180] #기준일로부터 6개월 이내의 구매기록이 있는 고객의 데이터만 추출. 

# Monetary
monetary_df = pd.DataFrame() # 구매금액 데이터 초기화
monetary_df['Monetary'] = df_6m.groupby("customer_id")["purchase_amt"].agg("sum") #고객 아이디별 구매금액 합산 

# Frequency
freq = df_6m[['customer_id','purchase_id']].drop_duplicates() # 고객 아이디와 구매아이디만 추출한뒤 중복 제거
frequency_df = freq.groupby('customer_id')['purchase_id'].count().reset_index() ## 아이디로 그룹화 한다음 방문횟수를 구해야 한다. 여기서는 방문횟수를 구매 아이디 개수로 생각했으므로 구매아이디에 count를 적용한다.
frequency_df = frequency_df.rename(columns={'purchase_id':'Frequency'})


# In[9]:


# Recency, Frequency, Monetary 데이터를 고객아이디를 기준으로 합침. 
rfm_df_6m = pd.merge(recency_df,frequency_df,how='inner',on='customer_id')
rfm_df_6m = pd.merge(rfm_df_6m,monetary_df,how='inner',on='customer_id')


# In[10]:


rfm_df_6m


# In[11]:


rfm_df_6m.describe().round(0)


# # R, F, M  점수 부여

# In[12]:


#RFM Class 

def recency_R(x):  #최근성 
    if 0<x<=30: return 6
    elif 30<x<=60: return 5
    elif 60<x<=90: return 4
    elif 90<x<=120: return 3
    elif 120<x<=150: return 2
    elif 150<x<=180: return 1
    else: return 0

def frequency_F(x):  #구매횟수 
    if 0<x<=1: return 0
    elif 1<x<=2: return 1
    elif 2<x<=3: return 2
    elif 3<x<=4: return 3
    elif 4<x<=7: return 4
    elif 7<x<=11: return 5
    else: return 6

def monetary_M(x):  #구매금액 
    if 0<x<=10000: return 0
    elif 10000<x<=20000: return 1
    elif 20000<x<=42000: return 2
    elif 42000<x<=62000: return 3
    elif 62000<x<=140000: return 4
    elif 140000<x<=192000: return 5
    else: return 6


# In[13]:


# R, F, M 점수 부여 
rfm_table = pd.DataFrame()
rfm_table["R"] = rfm_df_6m["Recency"].apply(recency_R)
rfm_table["F"] = rfm_df_6m["Frequency"].apply(frequency_F)
rfm_table["M"] = rfm_df_6m["Monetary"].apply(monetary_M)


# In[14]:


rfm_total = pd.concat([rfm_df_6m, rfm_table], axis=1)
rfm_total


# # RFM 가중치 설정 및 RFM score 계산

# In[15]:


# 가중치 설정
w1 = 0.35  #R에 대한 가중치 
w2 = 0.4  #F에 대한 가중치 
w3 = 0.25  #M에 대한 가중치 

def rfm_scoring(x,y,z):
    return x + y + z

def recency(x):
    return w1*x

def frequency(y):
    return w2*y

def monetary(z):
    return w3*z

w1_x=rfm_total['R'].apply(recency)
w2_y=rfm_total['F'].apply(frequency)
w3_z= rfm_total['M'].apply(monetary)

rfm_score = pd.DataFrame({'RFM': rfm_scoring(w1_x, w2_y, w3_z)})  #RFM score 계산 


# In[16]:


rfm_score


# In[17]:


rfm_total = pd.concat([rfm_total, rfm_score], axis=1)
rfm_total


# In[18]:


rfm_total['RFM'].describe()


# # 회원 등급 세분화

# In[19]:


silver = rfm_total[rfm_total.RFM < 2]  


# In[20]:


silver.head()


# In[21]:


gold = rfm_total.loc[(rfm_total.RFM >= 2) & (rfm_total.RFM < 5)]


# In[22]:


gold.head()


# In[23]:


platinum = rfm_total.loc[(rfm_total.RFM >= 5) & (rfm_total.RFM < 6)]


# In[24]:


platinum.head()


# In[25]:


royal = rfm_total[rfm_total.RFM >= 6]


# In[26]:


royal.head()


# In[27]:


# 새로운 고객등급 세분화 
def grade(x):
    if x<2: return 'new_4Silver'
    elif 2<=x<5: return 'new_3Gold'
    elif 5<=x<6: return 'new_2Platinum'
    else: return 'new_1Royal'


rfm_grade = pd.DataFrame()
rfm_grade["new_grade"] = rfm_total["RFM"].apply(grade)


# In[28]:


rfm_grade.head()


# In[29]:


rfm_total_grade = pd.concat([rfm_total, rfm_grade], axis=1)
rfm_total_grade.head()


# In[30]:


# 기존 회원 등급 불러오기 
mem_df = pd.read_csv("jeju_member_전처리.csv" )


# In[31]:


mem_df.drop('Unnamed: 0', axis=1)


# In[32]:


orig_grade = pd.DataFrame()
orig_grade = mem_df[['customer_id', 'customer_grade']]


# In[33]:


rfm_total_grade = pd.merge(rfm_total_grade, orig_grade, how='inner', on= 'customer_id')
rfm_total_grade.head()


# In[34]:


# csv 파일로 저장하기 
rfm_total_grade.to_csv('rfm_6m.csv')


# ---> 기준일(2019-12-31)로부터 6개월치 데이터만 가지고 등급 재조정한 결과 

# In[35]:


# 기존 등급과 새로 조정한 등급에 대한 교차도표 

old_new = pd.crosstab(rfm_total_grade.customer_grade, rfm_total_grade.new_grade, margins=True)


# In[36]:


old_new


# # Contingency Plot (Mosaic Plot)

# In[37]:


from statsmodels.graphics.mosaicplot import mosaic
import matplotlib.pyplot as plt


# In[38]:


mosaic(rfm_total_grade.sort_values('new_grade'), ['customer_grade', 'new_grade'])

plt.rcParams['figure.figsize'] = [8,5]
plt.show()


# # 고객 1회 방문당 구매금액
# 
# 신규고객 n명 유치시 매출액이 얼마나 향상되는지 예측 가능

# In[39]:


# 2년치 데이터

df_2y = pd.DataFrame() # 구매금액 데이터 초기화
df_2y['sum_purchase_amt'] = df.groupby("customer_id")["purchase_amt"].agg("sum")


# In[40]:


freq_2y = df[['customer_id','purchase_id']].drop_duplicates() # 고객 아이디와 구매 아이디만 추출한뒤 중복 제거
frequency_2y_df = freq_2y.groupby('customer_id')['purchase_id'].count().reset_index() ## 아이디로 그룹화 한다음 방문횟수를 구해야 한다. 여기서는 방문횟수를 구매 아이디 개수로 생각했으므로 구매 아이디에 count를 적용한다.
frequency_2y_df = frequency_2y_df.rename(columns={'purchase_id':'Frequency'})

frequency_2y_df


# In[41]:


freq_amt_2y = pd.merge(frequency_2y_df, df_2y,how='inner',on='customer_id')


# In[42]:


freq_amt_2y.head()


# In[43]:


# 2년치 데이터 기준 :  고객 1회 방문당 평균 구매금액

mean_amt_2y = freq_amt_2y['sum_purchase_amt'].sum() / freq_amt_2y['Frequency'].sum() 
mean_amt_2y


# In[44]:


# 2018년 데이터 

df_2018 = df.loc[(df.purchase_date >= 360) & (df.purchase_date < 720)]
df_18 = pd.DataFrame()
df_18['sum_purchase_amt'] = df_2018.groupby("customer_id")["purchase_amt"].agg("sum")


# In[45]:


df_18.head()


# In[46]:


freq_18 = df_2018[['customer_id','purchase_id']].drop_duplicates() # 고객 아이디와 구매 아이디만 추출한뒤 중복 제거
frequency_18_df = freq_18.groupby('customer_id')['purchase_id'].count().reset_index() ## 아이디로 그룹화 한다음 방문횟수를 구해야 한다. 여기서는 방문횟수를 구매아이디 개수로 생각했으므로 구매아이디에 count를 적용한다.
frequency_18_df = frequency_18_df.rename(columns={'purchase_id':'Frequency'})

frequency_18_df.head()


# In[47]:


freq_amt_18 = pd.merge(frequency_18_df, df_18,how='inner',on='customer_id')


# In[48]:


# 2018년 데이터 기준 :  고객 1회 방문당 평균 구매금액

mean_amt_18 = freq_amt_18['sum_purchase_amt'].sum() / freq_amt_18['Frequency'].sum() 
mean_amt_18


# In[49]:


# 2019년 데이터 

df_2019 = df[df.purchase_date <= 360]
df_19 = pd.DataFrame()
df_19['sum_purchase_amt'] = df_2019.groupby("customer_id")["purchase_amt"].agg("sum")


# In[50]:


freq_19 = df_2019[['customer_id','purchase_id']].drop_duplicates() # 고객 아이디와 구매아이디만 추출한뒤 중복 제거
frequency_19_df = freq_19.groupby('customer_id')['purchase_id'].count().reset_index() ## 아이디로 그룹화 한다음 방문횟수를 구해야 한다. 여기서는 방문횟수를 구매아이디 개수로 생각했으므로 구매아이디에 count를 적용한다.
frequency_19_df = frequency_19_df.rename(columns={'purchase_id':'Frequency'})

frequency_19_df.head()


# In[51]:


freq_amt_19 = pd.merge(frequency_19_df, df_19,how='inner',on='customer_id')

# 2019년 데이터 기준 :  고객 1회 방문당 평균 구매금액

mean_amt_19 = freq_amt_19['sum_purchase_amt'].sum() / freq_amt_19['Frequency'].sum() 
mean_amt_19


# In[52]:


# 최근 6개월치 데이터 기준

df_6month = pd.DataFrame()
df_6month['sum_purchase_amt'] = df_6m.groupby("customer_id")["purchase_amt"].agg("sum")


# In[53]:


freq_6m = df_6m[['customer_id','purchase_id']].drop_duplicates() # 고객 아이디와 구매아이디만 추출한뒤 중복 제거
frequency_6m_df = freq_6m.groupby('customer_id')['purchase_id'].count().reset_index() ## 아이디로 그룹화 한다음 방문횟수를 구해야 한다. 여기서는 방문횟수를 구매아이디 개수로 생각했으므로 구매아이디에 count를 적용한다.
frequency_6m_df = frequency_6m_df.rename(columns={'purchase_id':'Frequency'})

frequency_6m_df.head()


# In[54]:


freq_amt_6m = pd.merge(frequency_6m_df, df_6month,how='inner',on='customer_id')

# 최근 6개월치 데이터 기준: 고객 1회 방문당 평균 구매금액 

mean_amt_6m = freq_amt_6m['sum_purchase_amt'].sum() / freq_amt_6m['Frequency'].sum() 
mean_amt_6m


# In[55]:


print("<고객 1회 방문당 평균 구매금액>")
print("2018-2019년: %.1f(원) \n2018년: %.1f(원) \n2019년: %.1f(원) \n6개월(2019년 7-12월): %.1f(원)" %(mean_amt_2y,mean_amt_18,mean_amt_19,mean_amt_6m))

