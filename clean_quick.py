import pandas as pd

df = pd.read_csv('playtype_p.csv')
df=df[df.year>=2014]

df.to_csv('playtype_p.csv',index=False)