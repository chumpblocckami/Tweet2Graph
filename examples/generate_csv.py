import numpy as np
import pandas as pd
from datetime import datetime
import time
from tqdm import tqdm
def generate(n_file, lenght_file,n_users):
    for j in tqdm(range(0,n_file), desc="Generating csv"):
        data = pd.DataFrame()
        for i in range(0,lenght_file):
            user_activity = [np.random.randint(0,n_users),np.random.randint(0,50),np.random.randint(0,10),np.random.randint(0,10)]
            data = data.append(pd.Series(user_activity),ignore_index=True)
        data.columns = ["user", "retweet", "quote", "reply"]
        data.to_csv("./examples/csv/"+str(round(datetime.timestamp(datetime.now())))+".csv",index=False)
        time.sleep(1)