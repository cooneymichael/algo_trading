# coding: utf-8
import sqlite3
import pandas as pd
db_path = Path('./../../../Data/Data/stocks.db')
import Path
from pathlib import Path
db_path = Path('./../../../Data/Data/stocks.db')
get_ipython().system('ls ../../../Data/Data/stocks.db')
con = sqlite3.connect(db_path)
cur = con.cursor()
ewy = pd.read_sql(query, con, index_col='Datetime')
query = 'SELECT Datetime, Close FROM History WHERE SecurityId = (SELECT SecurityId FROM Securities WHERE SecurityTicker = \'EWY\')'
ewy = pd.read_sql(query, con, index_col='Datetime')
ewy
type(ewy)
ewy
ewy.rolling(window_size=50, min_periods=50).mean()
ewy.rolling(window=50, min_periods=50).mean()
ewy.rolling(window=50, min_periods=50)
from functools import reduce
ewy.head(n=50)
ewy.head(n=50).mean()
sma = ewy.head(n=50).mean()
roll = ewy.rolling(window=50, min_periods=50)
roll
for i in roll:
    print(i)
roll
print(rol)
print(roll)
for i in roll:
    print(i, i-1)
for i in roll:
    print(i, '==', i-1)
roll
type(roll)
ewy.rolling(window=50, min_periods=50).mean()
ewy.head(n=10)
ewy.iloc[9]
ewy.iloc[10]
ewy.iloc[9] = 1000
ewy.head(n=10)
ewy[10:]
ewy[9:]
roll
roll.next()
roll.window
roll.first()
roll.first()
roll.first()
roll.step()
roll.step
ewy
ewy.ewm(span=20)
ewy.ewm(span=20).mean()
ewy
ewy = pd.read_sql(query, con, index_col='Datetime')
ewy
ewy.ewm(span=20).mean()
pd.DataFrame(data=[1,2,3])
pd.DataFrame(data=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])
x = pd.DataFrame(data=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20])
x.ewm(span=10).mean()
x['ema_t'] = x.ewm(span=10).mean()
x
x['ema'] = x['ema_t']
x
def f(df, roll, period):
    multiplier = 1-(2/1+period)
    for idx, roll in enumerate(roll):
        df['ema'][idx] = df['ema_t'] + df.iloc[idx-1]['ema_t'] * multiplier
f(x, x.rolling(window=1, min_period=1), 10)
f(x, x.rolling(window=1, min_periods=1), 10)
def f(df, roll, period):
    multiplier = 1-(2/1+period)
    for idx, roll in enumerate(roll):
        val = df['ema_t'] + df.iloc[idx-1]['ema_t'] * multiplier
        print(val)
f(x, x.rolling(window=1, min_periods=1), 10)
x
x.rolling(window=1, min_periods=1).first()
def f(df, roll, period):
    multiplier = 1-(2/(1+period))
    for idx, roll in enumerate(roll):
        val = df['ema_t'] + df.iloc[idx-1]['ema_t'] * multiplier
        print(val)
f(x, x.rolling(window=1, min_periods=1), 10)
r = x.rolling(window=1, min_periods=1)
x
r
r.first()
r = x.rolling(window=2, min_periods=2)
r.first()
r = x.rolling(window=1, min_periods=1)
r.first()
for i in r:
    print(i)
def f(df, roll, period):
    multiplier = 1-(2/(1+period))
    for idx, roll in enumerate(roll):
        val = roll.iloc[1]['ema_t'] + roll.iloc[0]['ema_t'] * multiplier
        print(val)
f(x, x.rolling(window=1, min_periods=1), 10)
f(x, x.rolling(window=2, min_periods=2), 10)
r = x.rolling(window=2, min_periods=2)
for i in r:
    print(i)
for i in r:
    print(i)
    print(i.iloc[0])
for i in r:
    print(i.iloc[0])
for i in r:
    print(i.iloc[0])
    print(i.iloc[1])
for i in r:
    print(i.iloc[0])
    print(i.iloc[:1])
for i in r:
    print(i.iloc[:0])
    print(i.iloc[:1])
for i in r:
    print(i.iloc[:0])
    print(i.iloc[:1])
    print('==========')
get_ipython().run_line_magic('', '')
for i in r:
    print(i.iloc[:0])
    print()
    print(i.iloc[:1])
    print('==========')
x
for i in r:
    print(i)
    print()
    print(i.iloc[:0])
    print()
    print(i.iloc[:1])
    print('==========')
for i in r:
    print(i)
    print()
    print(i.iloc[:1])
    print()
    print(i.iloc[:2])
    print('==========')
for i in r:
    print(i)
    print()
    print(i.iloc[:,0])
    print()
    print(i.iloc[:,1])
    print('==========')
for i in r:
    print(i.iloc[:,0])
    print()
    print(i.iloc[:,1])
    print('==========')
for i in r:
    print(i)
    print('==========')
for i in r:
    print(i.iloc[:,0])
    print(i.iloc[:,1])
    print('==========')
for i in r:
    print(i.iloc[:,:])
    print(i.iloc[:,1])
    print('==========')
for i in r:
    print(i.iloc[:,1])
    print(i.iloc[:,2])
    print('==========')
def f(df, roll, period):
    multiplier = 1-(2/(1+period))
    for idx, roll in enumerate(roll):
        val = roll.iloc[:,2]['ema_t'] + roll.iloc[:,1]['ema_t'] * multiplier
        print(val)
f(x, x.rolling(window=2, min_periods=2), 10)
def f(df, roll, period):
    multiplier = 1-(2/(1+period))
    for idx, roll in enumerate(roll):
        val = roll.iloc[:,2] + roll.iloc[:,1] * multiplier
        print(val)
f(x, x.rolling(window=2, min_periods=2), 10)
def f(df, roll, period):
    multiplier = 1-(2/(1+period))
    for idx, roll in enumerate(roll):
        val = roll.iloc[:,2] + roll.iloc[:,1] * multiplier
        print('val:', val)
f(x, x.rolling(window=2, min_periods=2), 10)
def f(df, roll, period):
    multiplier = 1-(2/(1+period))
    for idx, roll in enumerate(roll):
        val = roll.iloc[:,2] + (roll.iloc[:,1] * multiplier)
        print('val:', val)
f(x, x.rolling(window=2, min_periods=2), 10)
for i in r:
    print(i.iloc[:,1])
    print(i.iloc[:,2])
for i in r:
    print(i.iloc[:,1])
    print(i.iloc[:,2])
    print(i.iloc[:,1] + i.iloc[:,2])
    print('==========')
for i in r:
    print(i.iloc[:,1])
    print(i.iloc[:,2])
    print('SUM:')
    print(i.iloc[:,1] + i.iloc[:,2])
    print('==========')
def f(df, roll, period):
    multiplier = 1-(2/(1+period))
    for idx, roll in enumerate(roll):
        val = roll.iloc[:,2] + (roll.iloc[:,1] * multiplier)
        print('val:', val)
        print('VAL:', val.iloc[:,2])
f(x, x.rolling(window=2, min_periods=2), 10)
def f(df, roll, period):
    multiplier = 1-(2/(1+period))
    for idx, roll in enumerate(roll):
        val = roll.iloc[:,2] + (roll.iloc[:,1] * multiplier)
        print('val:', val)
f(x, x.rolling(window=2, min_periods=2), 10)
def f(df, roll, period):
    multiplier = 1-(2/(1+period))
    for idx, roll in enumerate(roll):
        rolls = roll.iloc[:,2] + (roll.iloc[:,1] * multiplier)
        print(rolls)
f(x, x.rolling(window=2, min_periods=2), 10)
def f(df, roll, period):
    multiplier = 1-(2/(1+period))
    for idx, roll in enumerate(roll):
        rolls = ((roll.iloc[:,2] * period) + (roll.iloc[:,1] *period * multiplier)) / period
        print(rolls)
f(x, x.rolling(window=2, min_periods=2), 10)
x.ewm(span=10)
x.ewm(span=10).first()
for i in x.ewm(span=10):
    print(i)
x.drop[['ema_t', 'ema']]
x.drop(['ema_t', 'ema'])
x.drop(['ema_t', 'ema'], axis=1)
x.drop(['ema_t', 'ema'], axis=1, inplace=True)
x
for i in x.ewm(span=10):

    print(i)
for i in x.ewm(span=10):
    print(i)
def ema(df, span, ):
    multiplier = 2/(1+period)
    init_sma = df.iloc[:span].mean()
    for i in iterrows:



x.iterrows()
def ema(df, span, ):
    multiplier = 2/(1+period)
    init_sma = df.iloc[:span].mean()
    for i in iterrows:



for i in x.iterrows():
    print(i)
for i in x.iterrows():
    print(i)
for i in x.iterrows():
    print(i['Close'])
for i in x.iterrows():
    print(i)
x
x = pd.DataFrame(data=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20], columns=['Close'])
x
for i in x.iterrows():
    print(i)
for i in x.iterrows():
    print(i[1])
for i in x.iterrows():
    print(i[1][0])
for i in x.iterrows():
    print(i[1].split(' '))
for i in x.iterrows():
    print(i[1])
for i in x.iterrows():
    print(i[1])
    print()
for i in x.iterrows():
    print(i[1].value)
    print()
for i in x.iterrows():
    print(i[1].values)
    print()
for i in x.iterrows():
    print(i[1].values[0])
    print()
def ema(df, span, ):
    multiplier = 2/(1+period)
    init_sma = df.iloc[:span].mean()
    for i in iterrows:
        val_t = i[1].values[0]
        ema = (val_t * multiplier) + (init_sma * (1-multiplier))
        df.loc['ema'] = ema
        init_sma = ema
def ema(df, span, ):
    multiplier = 2/(1+period)
    init_sma = df.iloc[:span].mean()
    for i in df.iloc[:span].iterrows:
        val_t = i[1].values[0]
        ema = (val_t * multiplier) + (init_sma * (1-multiplier))
        df.loc['ema'] = ema
        init_sma = ema
ema(x, 10)
def ema(df, span, period):
    multiplier = 2/(1+period)
    init_sma = df.iloc[:span].mean()
    for i in df.iloc[:span].iterrows:
        val_t = i[1].values[0]
        ema = (val_t * multiplier) + (init_sma * (1-multiplier))
        df.loc['ema'] = ema
        init_sma = ema
ema(x, 10, 10)
for i in x.iloc[:10].iterrows():
    print(i)
for i in x.iloc[10:].iterrows():
    print(i)
def ema(df, span):
    multiplier = 2/(1+span)
    init_sma = df.iloc[:span].mean()
    for i in df.iloc[span:].iterrows():
        val_t = i[1].values[0]
        ema = (val_t * multiplier) + (init_sma * (1-multiplier))
        df.loc['ema'] = ema
        init_sma = ema
ema(x, 10, 10)
ema(x, 10)
x
def ema(df, span):
    multiplier = 2/(1+span)
    init_sma = df.iloc[:span].mean()
    for i in df.iloc[span:].iterrows():
        val_t = i[1].values[0]
        ema = (val_t * multiplier) + (init_sma * (1-multiplier))
        df.loc['ema'] = ema
        init_sma = ema
    print(df)
ema(x, 10)
def ema(df, span):
    multiplier = 2/(1+span)
    init_sma = df.iloc[:span].mean()
    for idx, row in df.iloc[span:].iterrows():
        val_t = row.values[0]
        ema = (val_t * multiplier) + (init_sma * (1-multiplier))
        df.loc[idx, 'ema'] = ema
        init_sma = ema
    print(df)
ema(x, 10)
def ema(df, span):
    multiplier = 2/(1+span)
    init_sma = df.iloc[:span].mean()
    for idx, row in df.iloc[span:].iterrows():
        val_t = row.values[0]
        ema = (val_t * multiplier) + (init_sma * (1-multiplier))
        # df.loc[idx, 'ema'] = ema
        print(idx)
        init_sma = ema
    print(df)
ema(x, 10)
x = pd.DataFrame(data=[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20], columns=['Close'])
x
ema(x, 10)
ema(x, 10)
ema(x, 10)
def ema(df, span):
    multiplier = 2/(1+span)
    init_sma = df.iloc[:span].mean()
    for idx, row in df.iloc[span:].iterrows():
        val_t = row.values[0]
        ema = (val_t * multiplier) + (init_sma * (1-multiplier))
        df.loc[idx, 'ema'] = ema
        print(idx)
        init_sma = ema
    print(df)
x
ema(x, 10)
def ema(df, span):
    multiplier = 2/(1+span)
    init_sma = df.iloc[:span].mean()
    for idx, row in df.iloc[span:].iterrows():
        val_t = row.values[0]
        ema = (val_t * multiplier) + (init_sma * (1-multiplier))
        df.iloc[idx]['ema'] = ema
        print(idx)
        init_sma = ema
    print(df)
ema(x, 10)
x
def ema(df, span):
    multiplier = 2/(1+span)
    init_sma = df.iloc[:span].mean()
    for idx, row in df.iloc[span:].iterrows():
        val_t = row.values[0]
        ema = (val_t * multiplier) + (init_sma * (1-multiplier))
        df.iloc[idx]['ema'] = ema
        print(ema)
        init_sma = ema
    print(df)
ema(x, 10)
def ema(df, span):
    multiplier = 2/(1+span)
    init_sma = df.iloc[:span].mean()
    for idx, row in df.iloc[span:].iterrows():
        val_t = row.values[0]
        ema = (val_t * multiplier) + (init_sma * (1-multiplier))
        print(ema)
        # df.iloc[idx]['ema'] = ema
        init_sma = ema
    print(df)
ema(x, 10)
def ema(df, span):
    multiplier = 2/(1+span)
    init_sma = df.iloc[:span].mean()
    for idx, row in df.iloc[span:].iterrows():
        val_t = row.values[0]
        print(val_t)
        ema = (val_t * multiplier) + (init_sma * (1-multiplier))
        # print(ema)
        # df.iloc[idx]['ema'] = ema
        init_sma = ema
    print(df)
ema(x, 10)
def ema(df, span):
    multiplier = 2/(1+span)
    init_sma = df.iloc[:span].mean()
    for idx, row in df.iloc[span:].iterrows():
        val_t = row.values[0]
        print(val_t)
        print(val_t * multiplier)
        ema = (val_t * multiplier) + (init_sma * (1-multiplier))
        # print(ema)
        # df.iloc[idx]['ema'] = ema
        init_sma = ema
    print(df)
ema(x, 10)
def ema(df, span):
    multiplier = 2/(1+span)
    init_sma = df.iloc[:span].mean()
    for idx, row in df.iloc[span:].iterrows():
        val_t = row.values[0]
        print(val_t)
        print(val_t * multiplier)
        print((val_t * multiplier) + (init_sma))
        ema = (val_t * multiplier) + (init_sma * (1-multiplier))
        # print(ema)
        # df.iloc[idx]['ema'] = ema
        init_sma = ema
    print(df)
ema(x, 10)
def ema(df, span):
    multiplier = 2/(1+span)
    init_sma = df.iloc[:span].mean()
    print(init_sma)
    return
    for idx, row in df.iloc[span:].iterrows():
        val_t = row.values[0]
        print(val_t)
        print(val_t * multiplier)
        print((val_t * multiplier) + (init_sma))
        ema = (val_t * multiplier) + (init_sma * (1-multiplier))
        # print(ema)
        # df.iloc[idx]['ema'] = ema
        init_sma = ema
    print(df)
ema(x, 10)
def ema(df, span):
    multiplier = 2/(1+span)
    init_sma = df['Close'].iloc[:span].mean()
    print(init_sma)
    return
    for idx, row in df.iloc[span:].iterrows():
        val_t = row.values[0]
        print(val_t)
        print(val_t * multiplier)
        print((val_t * multiplier) + (init_sma))
        ema = (val_t * multiplier) + (init_sma * (1-multiplier))
        # print(ema)
        # df.iloc[idx]['ema'] = ema
        init_sma = ema
    print(df)
ema(x, 10)
def ema(df, span):
    multiplier = 2/(1+span)
    init_sma = df['Close'].iloc[:span].mean()
    print(init_sma)
    for idx, row in df.iloc[span:].iterrows():
        val_t = row.values[0]
        print(val_t)
        print(val_t * multiplier)
        print((val_t * multiplier) + (init_sma))
        ema = (val_t * multiplier) + (init_sma * (1-multiplier))
        # print(ema)
        # df.iloc[idx]['ema'] = ema
        init_sma = ema
    print(df)
ema(x, 10)
def ema(df, span):
    multiplier = 2/(1+span)
    init_sma = df['Close'].iloc[:span].mean()
    for idx, row in df.iloc[span:].iterrows():
        val_t = row.values[0]
        ema = (val_t * multiplier) + (init_sma * (1-multiplier))
        print(ema)
        # df.iloc[idx]['ema'] = ema
        init_sma = ema
    print(df)
ema(x, 10)
def ema(df, span):
    multiplier = 2/(1+span)
    init_sma = df['Close'].iloc[:span].mean()
    for idx, row in df.iloc[span:].iterrows():
        val_t = row.values[0]
        ema = (val_t * multiplier) + (init_sma * (1-multiplier))
        df.iloc[idx]['ema'] = ema
        init_sma = ema
    print(df)
ema(x, 10)
def ema(df, span):
    multiplier = 2/(1+span)
    init_sma = df['Close'].iloc[:span].mean()
    for idx, row in df.iloc[span:].iterrows():
        val_t = row.values[0]
        ema = (val_t * multiplier) + (init_sma * (1-multiplier))
        df.loc[idx, 'ema'] = ema
        init_sma = ema
    print(df)
ema(x, 10)
correct_results = [3,2.818,2.851,3.06,3.413,3.883,4.45,5.095,5.805,6.386,7.043,7.763,8.533,9.345,10.192,11.066,11.963]
