import urllib.request
import json
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as dates

response = urllib.request.urlopen('http://siika.es:1337/motion')
data = json.load(response)

# Parameters
year = 2017
month = 10
day = 16
hour_max = 24
hour_min = 6

locator = dates.HourLocator(range(0, 24, 1))
formatter = dates.DateFormatter('%H')

df = pd.DataFrame(data)

df['year'] = pd.Series(np.ones(df.__len__()), index=df.index)
df['month'] = pd.Series(np.ones(df.__len__()), index=df.index)
df['day'] = pd.Series(np.ones(df.__len__()), index=df.index)
df['hour'] = pd.Series(np.ones(df.__len__()), index=df.index)
df['minute'] = pd.Series(np.ones(df.__len__()), index=df.index)

for i in range(0,df.__len__()):
    df.at[i, 'createdAt'] = df.at[i, 'createdAt'][:-1] # Remove 'Z' at the end of the timestamps
    df.at[i, 'createdAt'] = datetime.strptime(df.at[i, 'createdAt'], "%Y-%m-%dT%H:%M:%S.%f") # Set datetime format
    time = df.at[i, 'createdAt']
    df.at[i, 'rel_change'] = float(df.at[i, 'rel_change']) # Convert string values to float

    # Set new column values
    df.at[i, 'year'] = time.year
    df.at[i, 'month'] = time.month
    df.at[i, 'day'] = time.day
    df.at[i, 'hour'] = time.hour
    df.at[i, 'minute'] = time.minute

# Get data from one day
df = df.loc[df['year'] == year]
df = df.loc[df['month'] == month]
df = df.loc[df['day'] == day]
df = df.loc[df['hour'] < hour_max]
df = df.loc[df['hour'] > hour_min]

# Set y axis height
y_height = df['rel_change'].max()

# Separate images
first = df.loc[df['location'] == '0']
second = df.loc[df['location'] == '1']

plt.gca().xaxis.set_major_formatter(formatter)
plt.gca().xaxis.set_major_locator(locator)
plt.ylim((0,y_height))
plt.plot(first['createdAt'],first['rel_change'])
plt.gcf().autofmt_xdate()
plt.savefig('first.png')

plt.figure(2)
plt.gca().xaxis.set_major_formatter(formatter)
plt.gca().xaxis.set_major_locator(locator)
plt.ylim((0,y_height))
plt.plot(second['createdAt'],second['rel_change'])
plt.gcf().autofmt_xdate()
plt.savefig('second.png')