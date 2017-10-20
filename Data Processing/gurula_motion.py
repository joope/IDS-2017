import urllib.request
import json
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as dates
import pytz
import sys

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

    for i in range(0, df.__len__()):
        df.at[i, 'createdAt'] = df.at[i, 'createdAt'][:-1]  # Remove 'Z' at the end of the timestamps
        df.at[i, 'createdAt'] = datetime.strptime(df.at[i, 'createdAt'], "%Y-%m-%dT%H:%M:%S.%f")  # Set datetime format
        time = df.at[i, 'createdAt']
        time = time.replace(tzinfo=utc)  # Set the time we got to utc
        time = time.astimezone(tz)  # Convert time to Helsinki timezone
        time = time.replace(tzinfo=utc)  # Plot doesn't handle timezones well. Make it think that the time is in utc
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
    df = df.loc[df['hour'] < hour_max]
    df = df.loc[df['hour'] >= hour_min]
    return df

def line_plot(df, change_type, image_name):

    locator = dates.HourLocator(range(0, 24, 1))
    formatter = dates.DateFormatter('%H')

    # Set y axis height
    y_height = df[change_type].max()

    plt.gca().xaxis.set_major_formatter(formatter)
    plt.gca().xaxis.set_major_locator(locator)
    plt.ylim((0,y_height))
    plt.plot(first['createdAt'],first[change_type])
    plt.savefig(image_name)

    plt.figure(2)
    plt.gca().xaxis.set_major_formatter(formatter)
    plt.gca().xaxis.set_major_locator(locator)
    plt.ylim((0,y_height))
    plt.plot(second['createdAt'],second[change_type])
    plt.savefig(image_name)

if __name__ == "__main__":

    # Parameters
    if sys.argv.__len__() < 9:
        year = 2017
        month = 10
        day = 20
        hour_min = 8
        hour_max = 19
        change_type = 'thresh_change'
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

    df = filter(df, year, month, day, hour_min, hour_max)

    # Separate images
    first = df.loc[df['location'] == '0']
    second = df.loc[df['location'] == '1']

    if plot_type == 'Line':
        line_plot(first, change_type, image_name + '_1.png')
        plt.figure(2)
        line_plot(second, change_type, image_name + '_2.png')