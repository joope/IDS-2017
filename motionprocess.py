import urllib.request
import json
import pandas as pd
import numpy as np
from datetime import datetime
from datetime import timedelta
import matplotlib as mpl
# Allows generating plots without display device
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import seaborn as sns
import pytz
import sys
import os

folder = 'public'

def get_data():
    response = urllib.request.urlopen('http://siika.es:1337/motion')
    data = json.loads(response.read().decode())
    return data

def normalize(data):
    tz = pytz.timezone('Europe/Helsinki')
    utc = pytz.timezone('UTC')

    df = pd.DataFrame(data)

    df['year'] = pd.Series(np.ones(df.__len__()), index=df.index)
    df['month'] = pd.Series(np.ones(df.__len__()), index=df.index)
    df['day'] = pd.Series(np.ones(df.__len__()), index=df.index)
    df['hour'] = pd.Series(np.ones(df.__len__()), index=df.index)
    df['minute'] = pd.Series(np.ones(df.__len__()), index=df.index)
    df['createdAt2'] = pd.to_datetime(df['createdAt'])
    df['createdAt'] = df['createdAt2']

    for i in range(0, df.__len__()):
        #df.at[i, 'createdAt'] = df.at[i, 'createdAt'][:-1]  # Remove 'Z' at the end of the timestamps
        #df.at[i, 'createdAt'] = datetime.strptime(df.at[i, 'createdAt'], "%Y-%m-%dT%H:%M:%S.%f")  # Set datetime format
        time = df.at[i, 'createdAt']
        time = time.replace(tzinfo=utc)  # Set the time we got to utc
        time = time.astimezone(tz)  # Convert time to Helsinki timezone
        time = time.replace(tzinfo=utc)  # Plot doesn't handle timezones well. Make it think that the time is in utc
        #pd.to_datetime(df['createdAt']).loc[pd.to_datetime(df['createdAt']) > minTime]
        df.at[i, 'createdAt'] = time

        # Set new column values
        df.at[i, 'year'] = time.year
        df.at[i, 'month'] = time.month
        df.at[i, 'day'] = time.day
        df.at[i, 'hour'] = time.hour
        df.at[i, 'minute'] = time.minute

        df.at[i, change_type] = float(df.at[i, change_type])  # Convert string values to float
    return df

def filter(df, year, month, day, hour_min, hour_max):
    # Get data from one day
    df = df.loc[df['year'] == year]
    df = df.loc[df['month'] == month]
    df = df.loc[df['day'] == day]
    df = df.loc[df['hour'] <= hour_max]
    df = df.loc[df['hour'] >= hour_min]
    return df

def filter_last_hours(df, hours):
    now = datetime.now()
    minTime = now - timedelta(hours=hours)
    df = df.loc[df['createdAt'] > minTime]
    return df

def line_plot(df, change_type, image_name):

    mean = df[change_type].rolling(30).mean()
    change_type = 'mean'
    locator = dates.HourLocator(range(0, 24, 1))
    formatter = dates.DateFormatter('%H')

    # Set y axis height
    y_height = mean.max()
    plt.figure(figsize=(20,10))
    plt.gca().xaxis.set_major_formatter(formatter)
    plt.gca().xaxis.set_major_locator(locator)
    plt.ylim((0,y_height))
    plt.plot(df['createdAt'],mean)
    plt.savefig(os.path.join(folder, image_name), bbox_inches='tight')


if __name__ == "__main__":

    # Parameters
    if sys.argv.__len__() < 9:
        now = datetime.now()
        minTime = now - timedelta(hours=8)
        year = now.year
        month = now.month
        day = now.day
        hour_min = minTime.hour
        hour_max = now.hour
        change_type = 'rel_change'
        plot_type = 'Line'
        image_name = 'line'
    else:
        year = int(sys.argv[1])
        month = int(sys.argv[2])
        day = int(sys.argv[3])
        hour_min = int(sys.argv[4])
        hour_max = int(sys.argv[5])
        change_type = sys.argv[6]
        plot_type = sys.argv[7]
        image_name = sys.argv[8]

    data = get_data()

    df = normalize(data)
    #
    # df = filter(df, year, month, day, hour_min, hour_max)
    df = filter_last_hours(df, 8)

    # Separate images
    first = df.loc[df['location'] == '0']
    second = df.loc[df['location'] == '1']

    if plot_type == 'Line':
        line_plot(first, change_type, image_name + '_1.png')
        plt.figure(2)
        line_plot(second, change_type, image_name + '_2.png')
    if plot_type == 'Bar':
        second = pd.DataFrame(first[change_type].astype(float))
        second['day'] = first['day']
        hour_bars = second.groupby(second['day'])['rel_change'].mean()
        hour_bars.plot.bar()
        plt.savefig(image_name, bbox_inches='tight')

    df = normalize(data)
    df=df[['rel_change','hour']]
    grouped_df = df.groupby('hour')
    mean_df = grouped_df.sum()/ grouped_df.count()
  
    plt.figure(figsize=(20, 10))
    fig= sns.regplot(df.hour, df.rel_change, lowess=True, color='g')
    fig.axes.set_title('Activity trend line', fontsize=30,color="r",alpha=0.5)
    fig.set_xlabel("Hours")
    fig.set_ylabel("Activity")
    plt.savefig(os.path.join(folder, 'activity_trend.png'), bbox_inches='tight')
   
    plt.figure(figsize=(5, 5))
    fig=mean_df.plot(kind='bar', colormap='jet', title='Average activity by hour')
    fig.set_xlabel("Hours")
    fig.set_ylabel("Activity")
    plt.savefig('Activity.png', bbox_inches='tight')
    plt.savefig(os.path.join(folder, 'activity.png'), bbox_inches='tight')
    #mean_df['rel_change'].plot(color = 'orange',linewidth=2.0)
    #plt.savefig(image_name, bbox_inches='tight')
    #mean_df['hour'] =[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
    #maxi=mean_df.loc[mean_df['rel_change'].idxmax()]
    ##(maxi.hour,maxi.rel_change) is the maximum point in the last plot.
