import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style('whitegrid')
plt.style.use("fivethirtyeight")

from pandas_datareader.data import DataReader
import yfinance as yf
from pandas_datareader import data as pdr
from datetime import datetime
import streamlit as st
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf

yf.pdr_override()

end = datetime.now()
start = datetime(end.year - 10, end.month, end.day)

st.title('Stock Trend Prediction')

user_input = st.text_input('Enter Stock Ticker', 'AAPL')

df = yf.download(user_input, start, end)

# Describe data
st.subheader('Data from {} - {}'.format(str(start.date()),str(end.date())))
st.write(df.describe())

# Visualization
st.subheader('Closing price vs Time chart')
fig = plt.figure(figsize=(12,6))
plt.plot(df.Close, 'b')
st.pyplot(fig)

# Moving Averages
st.subheader('Closing price vs Time chart with 100MA')
ma100 = df.Close.rolling(100).mean()
fig = plt.figure(figsize=(12,6))
plt.plot(ma100, 'r')
plt.plot(df.Close, 'b')
st.pyplot(fig)

st.subheader('Closing price vs Time chart with 100MA & 200MA')
ma100 = df.Close.rolling(100).mean()
ma200 = df.Close.rolling(200).mean()
fig = plt.figure(figsize=(12,6))
plt.plot(ma100, 'r')
plt.plot(ma200, 'g')
plt.plot(df.Close, 'b')
st.pyplot(fig)

st.subheader('Daily Returns')

df['Daily Return'] = df['Adj Close'].pct_change()
fig = plt.figure(figsize=(12,6))
df['Daily Return'].plot(legend=True, linestyle='--', marker='o')
plt.ylabel('% Change')
plt.title('Daily Return')
st.pyplot(fig)

fig = plt.figure(figsize=(12, 6))
df['Daily Return'].hist(bins=50)
plt.xlabel('Daily Return')
plt.ylabel('Counts')
st.pyplot(fig)


data_training = pd.DataFrame(df['Close'][0:int(len(df)*0.70)])
data_testing = pd.DataFrame(df['Close'][int(len(df)*0.70): int(len(df))])

scaler = MinMaxScaler(feature_range=(0,1))

# Load Model
model = tf.keras.models.load_model('apple_tf')

data_training_array = scaler.fit_transform(data_training)
past_100_days = data_training.tail(100)
final_df = pd.concat([past_100_days, data_testing], ignore_index=True)
input_data = scaler.fit_transform(final_df)

x_test = []
y_test = []

for i in range(100, input_data.shape[0]):
  x_test.append(input_data[i-100: i])
  y_test.append(input_data[i, 0])

x_test, y_test = np.array(x_test), np.array(y_test)

y_predicted = model.predict(x_test)

scale_factor = 1/scaler.scale_[0]

y_predicted = y_predicted * scale_factor
y_test = y_test * scale_factor

# Final Prediction
st.subheader('Prediction vs Original')
fig = plt.figure(figsize=(12,6))
plt.plot(y_test,'b', label='Original Price')
plt.plot(y_predicted,'r',label='Predicted Price')
plt.xlabel('Time')
plt.ylabel('Price')
plt.legend()
st.pyplot(fig)

