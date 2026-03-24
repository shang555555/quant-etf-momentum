import pandas as pd

#std 标准差
def run_mean_reversion(prices,window=20,std_n=2, verbose=False):
    prices=prices.dropna()

    ma=prices.rolling(window).mean()
    std=prices.rolling(window).std()

    upper=ma+std_n*std
    lower=ma-std_n*std
    
    #初始化持仓信号序列
    position=pd.Series(0,index=prices.index)

    #遍历价格，回到均线就卖出
    for i in range(1,len(prices)):
        
        #如果空仓
        if position.iloc[i-1]==0:

            if prices.iloc[i]<lower.iloc[i]:
                position.iloc[i]=1

            else:
                position.iloc[i]=0

        else:

            #回到均线卖出
            if prices.iloc[i]>ma.iloc[i]:
                position.iloc[i]=0
            else:
                position.iloc[i]=1

    #每日收益率
    returns=prices.pct_change(fill_method=None).fillna(0.0)

    #策略每日收益率
    strategy_returns=returns*position.shift(1)

    equity=(1+strategy_returns).cumprod()

    position_ratio = float(position.mean())
    trade_count = int((position.diff() == 1).sum())
    equity.attrs["position_ratio"] = position_ratio
    equity.attrs["trade_count"] = trade_count

    if verbose:
        print("持仓比例:", position_ratio)
        print("交易次数:", trade_count)

    return equity

    



