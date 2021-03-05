import numpy as np
import pandas as pd
from datetime import datetime
import time

if __name__ == "__main__":
    for j in range(0,100):
        data = pd.DataFrame()
        for i in range(0,1000):
            #33 utenti
            user_activity = [np.random.randint(0,33),np.random.randint(0,50),np.random.randint(0,10),np.random.randint(0,10)]
            data = data.append(pd.Series(user_activity),ignore_index=True)
        data.columns = ["user", "retweet", "quote", "reply"]
        data.to_csv("./csv/"+str(round(datetime.timestamp(datetime.now())))+".csv",index=False)
        time.sleep(1)