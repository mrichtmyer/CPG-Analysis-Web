import pandas as pd

df = pd.read_csv("data/emotion_csv/eucerin_intensive_lotion.csv")
df_dict = {col:df[col].tolist() for col in df}

print(df_dict)
# for col in df:
#     df_dict[col] = df[col].tolist()
#print(df.head())