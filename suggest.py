import numpy as np
import pandas as pd
import yfinance as yf

def etf():
    STOCK_DAILY_PRICE = pd.read_csv('csv/NH_CONTEST_STK_DT_QUT.csv',encoding="euc-kr")
    NW_FC_STK_IEM_IFO = pd.read_csv('csv/NH_CONTEST_NW_FC_STK_IEM_IFO.csv',encoding="euc-kr")
    STOCK_DAILY = pd.read_csv('csv/NH_CONTEST_NHDATA_STK_DD_IFO.csv',encoding="euc-kr")
    NHDATA_IFW_OFW_IFO = pd.read_csv('csv/NH_CONTEST_NHDATA_IFW_OFW_IFO.csv',encoding="euc-kr")
    CUSTOMER = pd.read_csv('csv/NH_CONTEST_NHDATA_CUS_TP_IFO.csv',encoding="euc-kr")
    ETF_SCORE = pd.read_csv('csv/NH_CONTEST_ETF_SOR_IFO.csv',encoding="euc-kr")
    DIVIDEND = pd.read_csv('csv/NH_CONTEST_DATA_HISTORICAL_DIVIDEND.csv',encoding="euc-kr")
    DATA_ETF_HOLDINGS = pd.read_csv('csv/NH_CONTEST_DATA_ETF_HOLDINGS.csv',encoding="euc-kr")

    def calculate_score(data):
        data = np.array(data)
        mean = np.mean(data)
        std = np.std(data)
        scores = (data - mean) / std
        scores = scores * 15 + 100
        return scores.tolist()

    ETF_SCORE['ticker'] = ETF_SCORE['etf_iem_cd'].str.strip()
    etf_list = ETF_SCORE['ticker'].unique()
    etf_list.sort()

    STOCK_DAILY_PRICE['ticker'] = STOCK_DAILY_PRICE['tck_iem_cd'].str.strip()
    DIVIDEND['ticker'] = DIVIDEND['etf_tck_cd'].str.strip()
    DIVIDEND['paid_date'] = pd.to_datetime(DIVIDEND['ddn_pym_dt'], format='%Y%m%d')

    etf_stability_list = []
    etf_growth_list = []
    etf_dividend_list = []
    etf_liquidity_list = []
    etf_variety_list = []
    etf_sector_list = []
    for etf in etf_list:
        etf_df = STOCK_DAILY_PRICE[STOCK_DAILY_PRICE['ticker'] == etf]
        etf_stability_list.append(etf_df['bf_dd_cmp_ind_rt'].std())

        etf_div_df = DIVIDEND[DIVIDEND['ticker'] == etf]
        if etf_div_df.empty:
            etf_dividend_list.append(0)
        else:
            etf_div_df.sort_values(by=['paid_date'])

            yields = []
            for date in etf_div_df['paid_date']:
                yf_data = yf.download(etf, start=date, end=date + pd.Timedelta(days=1), progress=False)
                newdate = date
                if not yf_data.empty:
                    yields.append(float(etf_div_df[etf_div_df['paid_date'] == date].iloc[0]['ddn_amt']) / yf_data['Close'].iloc[0])
                else:
                    while yf_data.empty:
                        newdate = newdate - pd.Timedelta(days=1)
                        yf_data = yf.download(etf, start=newdate, end=newdate + pd.Timedelta(days=1))
                    try:
                        yields.append(float(etf_div_df[etf_div_df['paid_date'] == date].iloc[0]['ddn_amt']) / yf_data['Close'].iloc[0])
                    except:
                        print(etf_div_df[etf_div_df['paid_date'] == date])
                        print(yf_data)
            try:
                avg_yield = pd.array(yields).mean()
            except:
                raise Exception('avg_yield error')

            try:
                if etf_div_df.iloc[0]['ddn_pym_fcy_cd'] == 'Quarterly':
                    etf_dividend_list.append(avg_yield * 4)
                elif etf_div_df.iloc[0]['ddn_pym_fcy_cd'] == 'Monthly':
                    etf_dividend_list.append(avg_yield * 12)
                elif etf_div_df.iloc[0]['ddn_pym_fcy_cd'] == 'Annual':
                    etf_dividend_list.append(avg_yield)
                elif etf_div_df.iloc[0]['ddn_pym_fcy_cd'] == 'SemiAnnual':
                    etf_dividend_list.append(avg_yield * 2)
                else:
                    etf_dividend_list.append(pd.array(yields).sum() / (etf_div_df.iloc[-1]['paid_date'] - etf_div_df.iloc[0]['paid_date']).days / 365)
            except:
                print(etf_div_df)
                print(etf)
                raise Exception('dividend error')
        etf_liquidity_list.append(etf_df['acl_trd_qty'].mean())

        etf_score_df = ETF_SCORE[ETF_SCORE['ticker'] == etf]
        etf_growth_list.append(etf_score_df['yr1_tot_pft_rt'].mean())

    etf_stab = np.array(etf_stability_list)
    stab_mean = np.mean(etf_stab)
    etf_stab = (etf_stab - stab_mean) / np.std(etf_stab)
    etf_stab = -etf_stab #편차가 적은 ETF가 점수가 더 높게 나오도록 부호 바꿔주기
    etf_stab = etf_stab * 15 + 100 #IQ 점수 매기는 방식을 밴치마킹
    etf_stability_scores = etf_stab.tolist()

    etf_growth_scores = calculate_score(etf_growth_list)

    etf_dividend_scores = calculate_score(etf_dividend_list)

    etf_liquidity_scores = calculate_score(etf_liquidity_list)

    ETF_SCORE_DF = pd.DataFrame({'ticker': etf_list, 'stability': etf_stability_scores, 'growth': etf_growth_scores, 'dividend': etf_dividend_scores, 'liquidity': etf_liquidity_scores})

    def calculate_score(row):
        return (weight['stability'] * row['stability'] + weight['growth'] * row['growth'] + weight['dividend'] * row['dividend'] + weight['liquidity'] * row['liquidity']) / (weight['stability'] + weight['growth'] + weight['dividend'] + weight['liquidity'])

    ETF_SCORE_DF['score'] = ETF_SCORE_DF.apply(calculate_score, axis=1)
    ETF_SCORE_DF.sort_values(by=['score'], ascending=False, inplace=True)
    ETF_SCORE_DF.reset_index(drop=True, inplace=True)
    return ETF_SCORE_DF