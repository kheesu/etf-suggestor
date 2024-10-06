import streamlit as st
from openai import OpenAI
import numpy as np
import pandas as pd
import suggest
pd.options.mode.chained_assignment = None

# Show title and description.
st.title("ETF 추천 시스템")
st.write(
    "아래의 양식을 입력하면 당신에게 맞춤형 ETF를 소개해 드립니다.\n"
    "당신에게 아래의 특징이 얼마나 들어맞는지 생각하고 0에서 100 사이의 중요도를 입력해 주세요."
)
st.subheader('안정형')
stability = st.slider('당신은 하루에도 10%씩 오르고 내리는 종목을 가지고 버틸수 있다면 낮게, 안정적인 투자를 원한다면 높게 설정해 주세요.', 0, 100, 50)

st.subheader('성장형')
growth = st.slider('앞으로의 ETF의 성장에 지난 1년간의 수익률이 중요하다고 생각하면 높게 설정해 주세요', 0, 100, 50)

st.subheader('배당형')
dividend = st.slider('무엇보다 꾸준하게 나오는 배당금을 많이 받고 싶다면 높게 설정해 주세요.', 0, 100, 50)

st.subheader('유동형')
liquidity = st.slider('사람이 많이 찾는 이유가 있다고 생각하고 거래량이 많은 ETF를 선호하면 높게 설정해 주세요.', 0, 100, 50)

if st.button('추천받기!', type='primary'):
    suggest.weight = {
        'stability': stability/100,
        'growth': growth/100,
        'dividend': dividend/100,
        'liquidity': liquidity/100
    }
    with st.spinner('고객님에게 알맞는 ETF를 찾는 중...'):
        df = suggest.etf()
    st.balloons()
    st.write(df.head(10))

