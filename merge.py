import pandas as pd
import os

os.chdir('../2k23/')
df = pd.DataFrame()
for name in os.listdir():
    match = pd.read_csv(name)
    df = df.append(match, ignore_index=True)

df.to_csv('ipl2k23.csv')
