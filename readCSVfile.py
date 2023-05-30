import pandas as pd
import numpy as np

def readCSV():
    df=pd.read_csv('processed/embeddings.csv', index_col=0)
    df['embeddings'] = df['embeddings'].apply(eval).apply(np.array)
    df.head()
    return df