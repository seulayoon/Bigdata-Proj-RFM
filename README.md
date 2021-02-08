# Bigdata-Proj-RFM

맞춤형 제품 추천 및 회원 등급 재조정을 통한 유통회사 매출 증대

```
Data    
│
├── jeju_member.csv         - 회원 정보
└── jeju_sales.csv          - 구매 내역
```
<br/><br/>


## RFM Analysis

고객의 최근성(Recency), 구매빈도(Frequency), 구매금액(Monetary) 3가지 지표를 이용하여 고객의 가치를 분석하는 기법



1. RFM 분석을 통한 회원등급 세분화
2. 고객 1회 방문당 구매금액 계산 : 신규고객 n명 유치시 매출액이 얼마나 향상되는지 예측<br/><br/>



### 데이터

- __jeju_merge_sales.csv__:  jeju_sales.csv와 jeju_member.csv를 customer_id를 key로 병합
- 사용 변수: customer_id, purchase_id, purchase_date, purchase_amt



Frequency(구매 빈도): 구매 아이디당 구매 횟수로 간주하여 카운트

Recency(최근성): 기준일(2019-12-31)과 최근 구매일의 일수 차이 계산

Monetary(구매금액): 기간 내 총 구매금액 합산<br/><br/>



### 점수 기준

RFM score = w1 * R + w2 * F + w3 * M (w1 = 0.35, w2 = 0.4, w3 = 0.25)

*식자재를 많이 취급하는 마트의 특성 상 구매금액보다 상품회전률이 더 중요하므로 F의 가중치를 가장 크게 주고 M의 가중치를 가장 작게 설정<br/><br/>



### 등급 기준

Royal > Platinum > Gold > Silver<br/><br/>



### 분석 결과

기존의 회원 등급과 RFM 분석을 통해 새로 조정한 회원 등급에 대한 교차도표(Contingency Plot)

![Contingency Plot](https://user-images.githubusercontent.com/52132773/107232314-9db39d00-6a64-11eb-92fc-11e4c5bf55af.JPG)

