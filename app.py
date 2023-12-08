import matplotlib
matplotlib.use('Agg')  # Set the backend before importing pyplot

from flask import Flask, render_template, request
from flask import send_from_directory

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
import tensorflow as tf
import yfinance as yf

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/video-call')
def video_call():
    return render_template('video_calling.html')

@app.route('/room')
def room():
    return render_template('room.html')

@app.route('/predict', methods=['POST'])
def predict():
    user_input = request.form['ticker']

    end = datetime.now()
    start = datetime(end.year - 10, end.month, end.day)

    df = yf.download(user_input, start, end)

    # Describe data
    data_description = df.describe()

    # Visualization
    closing_price_chart = visualize_closing_price(df)
    closing_price_100ma_chart = visualize_closing_price_100ma(df)
    closing_price_100ma_200ma_chart = visualize_closing_price_100ma_200ma(df)
    daily_returns_chart = visualize_daily_returns(df)

    # Load Model
    model = tf.keras.models.load_model('apple_tf')

    data_training = pd.DataFrame(df['Close'][0:int(len(df)*0.5)])
    data_testing = pd.DataFrame(df['Close'][int(len(df)*0.5): int(len(df))])

    scaler = MinMaxScaler(feature_range=(0, 1))

    # data_training_array = scaler.fit_transform(data_training)
    past_100_days = data_training.tail(100)
    final_df = pd.concat([past_100_days,data_testing], ignore_index=True)
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
    past_100_days = past_100_days * scale_factor

    # Final Prediction
    prediction_vs_original_chart = visualize_prediction_vs_original(y_test, y_predicted, past_100_days)

    return render_template(
        'prediction.html',
        user_input=user_input,
        data_description=data_description.to_html(),
        closing_price_chart=closing_price_chart,
        closing_price_100ma_chart=closing_price_100ma_chart,
        closing_price_100ma_200ma_chart=closing_price_100ma_200ma_chart,
        daily_returns_chart=daily_returns_chart,
        prediction_vs_original_chart=prediction_vs_original_chart
    )

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('static', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

def visualize_closing_price(df):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df['Close'], 'b')
    ax.set_title('Closing price vs Time chart')
    chart_path = 'static/closing_price_chart.png'
    plt.savefig(chart_path)
    plt.close(fig)
    return chart_path

def visualize_closing_price_100ma(df):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df['Close'].rolling(100).mean(), 'r', label='100MA')
    ax.plot(df['Close'], 'b', label='Closing Price')
    ax.legend()
    ax.set_title('Closing price vs Time chart with 100MA')
    chart_path = 'static/closing_price_100ma_chart.png'
    plt.savefig(chart_path)
    plt.close(fig)
    return chart_path

def visualize_closing_price_100ma_200ma(df):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df['Close'].rolling(100).mean(), 'r', label='100MA')
    ax.plot(df['Close'].rolling(200).mean(), 'g', label='200MA')
    ax.plot(df['Close'], 'b', label='Closing Price')
    ax.legend()
    ax.set_title('Closing price vs Time chart with 100MA & 200MA')
    chart_path = 'static/closing_price_100ma_200ma_chart.png'
    plt.savefig(chart_path)
    plt.close(fig)
    return chart_path

def visualize_daily_returns(df):
    fig, ax = plt.subplots(figsize=(12, 6))
    df['Daily Return'] = df['Adj Close'].pct_change()
    df['Daily Return'].plot(legend=True, linestyle='--', marker='o')
    plt.ylabel('% Change')
    plt.title('Daily Return')
    chart_path = 'static/daily_returns_chart.png'
    plt.savefig(chart_path)
    plt.close(fig)
    return chart_path

def visualize_prediction_vs_original(y_test, y_predicted, past_100_days):
    fig, ax = plt.subplots(figsize=(12, 6))
    # ax.plot(past_100_days, 'g', label='Past 100 Days')
    ax.plot(y_test, 'b', label='Original Price')
    ax.plot(y_predicted, 'r', label='Predicted Price')
    ax.set_xlabel('Time')
    ax.set_ylabel('Price')
    ax.legend()
    ax.set_title('Prediction vs Original')
    chart_path = 'static/prediction_vs_original_chart.png'
    plt.savefig(chart_path)
    plt.close(fig)
    return chart_path

if __name__ == '__main__':
    app.run(debug=True)
