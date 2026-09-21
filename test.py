import pandas as pd

df = pd.read_excel("bitacora_sintetica.xlsx", sheet_name="Bitacora", header=[0, 1])
cols = list(df.columns[2:])
for mat in dict.fromkeys(top for top, _ in cols):
    print(mat, [sub for top, sub in cols if top == mat], "\n")