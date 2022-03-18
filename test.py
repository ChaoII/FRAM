import pandas as pd
from datetime import datetime


def del_df(df):
    df.sort_values(by='datetime', ascending=True)
    return df.iloc[[0, -1], :]


df = pd.read_excel("./attend/2022-03-16.xls", index_col=0)
time = datetime.now().strftime("%Y-%m-%d %H:%M:%S %f")

new_df = pd.DataFrame([["55543e87-b632-48ef-9879-6e37cd08da4a", "袁伟", time]], columns=["id", "name", "datetime"])
df = pd.concat([df, new_df], ignore_index=True)

# df = df.append(new_df, ignore_index=True)

ret_df = df.groupby("id").apply(del_df).reset_index(drop=True)
ret_df.to_excel("./attend/2022-03-16.xls")
