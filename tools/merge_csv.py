import pandas as pd
import glob
import os

path = r'data'                     # use your path
all_files = glob.glob(os.path.join(path, "*.csv"))

df_from_each_file = (pd.read_csv(f) for f in all_files)
df = pd.concat(df_from_each_file, ignore_index=True)

print(df)
df.to_csv("merge.csv", index=False)