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
    df['weekday'] = pd.Series(np.ones(df.__len__()), index=df.index)
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
        df.at[i, 'weekday'] = time.weekday()

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

def line_plot(df, change_type, image_name, y_height):

    mean = df[change_type].rolling(30).mean()
    change_type = 'mean'
    locator = dates.HourLocator(range(0, 24, 1))
    formatter = dates.DateFormatter('%H')

    # Set y axis height
    #y_height = mean.max()
    plt.figure(figsize=(20,10))
    plt.gca().xaxis.set_major_formatter(formatter)
    plt.gca().xaxis.set_major_locator(locator)
    plt.ylim((0.01,y_height))
    plt.plot(df['createdAt'],mean)
    plt.savefig(os.path.join(folder, image_name), bbox_inches='tight')

def bar_plot_weekday(df, change_type, image_name):
    grouped_by_column = 'weekday'
    df = df[[change_type, grouped_by_column]]
    grouped_df = df.groupby(grouped_by_column)
    mean_df = grouped_df.sum() / grouped_df.count()

    plt.figure(figsize=(20, 10))
    fig = mean_df.plot(kind='bar', colormap='jet', title='Average activity by ' + grouped_by_column, legend=None)
    fig.set_xlabel(grouped_by_column)
    fig.set_ylabel("Activity")
    plt.ylim(0.01, 0.05)
    plt.xticks([0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0], ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
    plt.savefig(os.path.join(folder, image_name), bbox_inches='tight')

def bar_plot_int(df, change_type, grouped_by_column, image_name):
    df = df[[change_type, grouped_by_column]]
    df['grouped'] = df[grouped_by_column].astype(int)
    grouped_df = df[[change_type, 'grouped']].groupby('grouped')
    mean_df = grouped_df.sum() / grouped_df.count()

    plt.figure(figsize=(20, 10))
    fig = mean_df.plot(kind='bar', colormap='jet', title='Average activity by ' + grouped_by_column, legend=None)
    fig.set_xlabel(grouped_by_column)
    fig.set_ylabel("Activity")
    plt.ylim(0.01, 0.05)
    plt.savefig(os.path.join(folder, image_name), bbox_inches='tight')

def activity_trend(df, change_type, image_name, y_height):
    df = df[['rel_change', 'hour']]
    grouped_df = df.groupby('hour')
    mean_df = grouped_df.sum() / grouped_df.count()

    plt.figure(figsize=(20, 10))
    fig = sns.regplot(df.hour, df.rel_change, lowess=True, color='g')
    fig.axes.set_title('Activity trend line', fontsize=30, color="r", alpha=0.5)
    fig.set_xlabel("Hours")
    fig.set_ylabel("Activity")
    plt.ylim(0.01, y_height)
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

    normalized = normalize(data)

    y_height = normalized[change_type].rolling(30).mean().max()

    normalized_first = normalized.loc[normalized['location'] == '0']
    normalized_second = normalized.loc[normalized['location'] == '1']
    #
    # df = filter(df, year, month, day, hour_min, hour_max)
    first = filter_last_hours(normalized_first, 8)
    second = filter_last_hours(normalized_second, 8)

    plt.figure(figsize=(20, 10))
    line_plot(first, change_type, 'line_1.png', y_height)
    plt.figure(figsize=(20, 10))
    line_plot(second, change_type, 'line_2.png', y_height)

    bar_plot_int(normalized_first, change_type, 'hour', 'activity_by_hour_1')
    bar_plot_int(normalized_second, change_type, 'hour', 'activity_by_hour_2')
    bar_plot_weekday(normalized_first, change_type, 'activity_by_day_1')
    bar_plot_weekday(normalized_second, change_type, 'activity_by_day_2')

    y_height = normalized[change_type].max()

    activity_trend(normalized_first, change_type, 'activity_trend_1', y_height)
    activity_trend(normalized_second, change_type, 'activity_trend_2', y_height)

    #mean_df['rel_change'].plot(color = 'orange',linewidth=2.0)
    #plt.savefig(image_name, bbox_inches='tight')
    #mean_df['hour'] =[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
    #maxi=mean_df.loc[mean_df['rel_change'].idxmax()]
    ##(maxi.hour,maxi.rel_change) is the maximum point in the last plot.
