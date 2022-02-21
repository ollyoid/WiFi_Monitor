
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
import datetime

import io
from PIL import Image

def create_plot(log="log.csv"):
    df = pd.read_csv(log, on_bad_lines='skip')
    # Convert the date to an understandable format
    df['timestamp'] = pd.to_datetime(df['timestamp'], format='%Y-%m-%dT%H:%M:%S.%fZ')
    df['seconds'] = df['timestamp'].astype(np.int64)
    df = df.set_index('timestamp')


    now = round(datetime.datetime.now().timestamp())
    start = round(max(df['seconds'].min()/1000000000, now-(24*60*60)))

    roll = round((now-start)/48)

    # Get rolling average (smooth) the data.
    rolling = df[['upload', 'download', 'ping']].rolling(f'{round(roll)}s').mean()
    df['upload_r'] = rolling['upload']
    df['download_r'] = rolling['download']
    df['ping_r'] = rolling['ping']

    upload_curve = interp1d(df['seconds'], df['upload_r'], kind = 'cubic')
    download_curve = interp1d(df['seconds'], df['download_r'], kind = 'cubic')
    ping_curve = interp1d(df['seconds'], df['ping_r'], kind = 'cubic')

        
    # Returns evenly spaced numbers over upto last day.
    X_ = np.linspace(max(df['seconds'].min(), now-(24*60*60)*100000000), df['seconds'].max(), 1000)

    fig, ax1 = plt.subplots(figsize=(12, 7.2), tight_layout=True)

    # Plot upload and  download against one axis
    ax1.plot(X_, upload_curve(X_)/1000000, linewidth=5, linestyle='dotted', color='k')
    ax1.plot(X_, download_curve(X_)/1000000, linewidth=3, linestyle='dashed', color='k')
    ax1.set_ylim(ymin=0)

    # Plot ping against the other axis
    ax2 = ax1.twinx()
    ax2.plot(X_, ping_curve(X_), linewidth=3, linestyle='dashdot', color='k')
    ax2.set_ylim(ymin=0)

    ax1.spines['top'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax1.xaxis.set_visible(False)
    ax2.xaxis.set_visible(False)
    ax1.get_yaxis().set_tick_params(direction='in', labelsize=20, pad=-35)
    ax2.get_yaxis().set_tick_params(direction='in', labelsize=20, pad=-30)


def get_img():
    create_plot()
    img_buf = io.BytesIO()
    plt.savefig(img_buf, pad_inches=0, format='png')

    im = Image.open(img_buf)
    im = im.resize((400,240)).convert('1')
    return im


if __name__ == "__main__":
    create_plot("../logs/log.csv")
    img_buf = io.BytesIO()
    plt.savefig(img_buf, pad_inches=0, format='png')

    im = Image.open(img_buf)
    im = im.resize((400,240)).convert('1')
    im.show()
    plt.show()