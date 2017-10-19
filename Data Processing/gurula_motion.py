import urllib.request
import json
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import pytz

response = urllib.request.urlopen('http://siika.es:1337/motion')
data = json.loads(response.read().decode())

# Parameters
year = 2017
month = 10
day = 18
hour_max = 19
hour_min = 7
change_type = 'thresh_change'

locator = dates.HourLocator(range(0, 24, 1))
formatter = dates.DateFormatter('%H')
tz=pytz.timezone('Europe/Helsinki')
utc = pytz.timezone('UTC')

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
    time = time.replace(tzinfo=utc) # Set the time we got to utc
    time = time.astimezone(tz) # Convert time to Helsinki timezone
    time = time.replace(tzinfo=utc) # Plot doesn't handle timezones well. Make it think that the time is in utc
    df.at[i, 'createdAt'] = time

    # Set new column values
    df.at[i, 'year'] = time.year
    df.at[i, 'month'] = time.month
    df.at[i, 'day'] = time.day
    df.at[i, 'hour'] = time.hour
    df.at[i, 'minute'] = time.minute

    df.at[i, change_type] = float(df.at[i, change_type]) # Convert string values to float

# Get data from one day
df = df.loc[df['year'] == year]
df = df.loc[df['month'] == month]
df = df.loc[df['day'] == day]
df = df.loc[df['hour'] < hour_max]
df = df.loc[df['hour'] >= hour_min]

# Set y axis height
y_height = df[change_type].max()

# Separate images
first = df.loc[df['location'] == '0']
second = df.loc[df['location'] == '1']

plt.gca().xaxis.set_major_formatter(formatter)
plt.gca().xaxis.set_major_locator(locator)
plt.ylim((0,y_height))
plt.plot(first['createdAt'],first[change_type])
plt.savefig('first.png')

plt.figure(2)
plt.gca().xaxis.set_major_formatter(formatter)
plt.gca().xaxis.set_major_locator(locator)
plt.ylim((0,y_height))
plt.plot(second['createdAt'],second[change_type])
plt.savefig('second.png')
