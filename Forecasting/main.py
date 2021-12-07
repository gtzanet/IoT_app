import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import tensorflow as tf
from matplotlib import pyplot as plt
from fastapi import FastAPI, BackgroundTasks

app = FastAPI()

def create_time_features(df, target=None):
    """
    Creates time series features from datetime index
    """
    df['date'] = df.index
    df['hour'] = df['date'].dt.hour
    df['dayofweek'] = df['date'].dt.dayofweek
    df['quarter'] = df['date'].dt.quarter
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['dayofyear'] = df['date'].dt.dayofyear
    df['sin_day'] = np.sin(df['dayofyear'])
    df['cos_day'] = np.cos(df['dayofyear'])
    df['dayofmonth'] = df['date'].dt.day
    df['weekofyear'] = df['date'].dt.weekofyear
    X = df.drop(['date'], axis=1)
    if target:
        y = df[target]
        X = X.drop([target], axis=1)
        return X, y

    return X

def window_data(X, Y, window=7):
    '''
    The dataset length will be reduced to guarante all samples have the window, so new length will be len(dataset)-window
    '''
    x = []
    y = []
    for i in range(window-1, len(X)):
        x.append(X[i-window+1:i+1])
        y.append(Y[i])
    return np.array(x), np.array(y)

def prepare_data():	
    # We split our dataset to be able to evaluate our models

    air_pollution = pd.read_csv('air_pollution.csv', parse_dates=['date'])
    air_pollution.set_index('date', inplace=True)

    split_date = '2014-01-01'
    df_training = air_pollution.loc[air_pollution.index <= split_date]
    df_test = air_pollution.loc[air_pollution.index > split_date]
    print(f"{len(df_training)} days of training data \n {len(df_test)} days of testing data ")

    df_training.to_csv('training.csv')
    df_test.to_csv('test.csv')

    X_train_df, y_train = create_time_features(df_training, target='pollution_today')
    X_test_df, y_test = create_time_features(df_test, target='pollution_today')
    scaler = StandardScaler()
    scaler.fit(X_train_df)  # No cheating, never scale on the training+test!
    X_train = scaler.transform(X_train_df)
    X_test = scaler.transform(X_test_df)

    X_train_df = pd.DataFrame(X_train, columns=X_train_df.columns)
    X_test_df = pd.DataFrame(X_test, columns=X_test_df.columns)

    # For our dl model we will create windows of data that will be feeded into the datasets, for each timestemp T we will append the data from T-7 to T to the Xdata with target Y(t)
    BATCH_SIZE = 64
    BUFFER_SIZE = 100
    WINDOW_LENGTH = 24

    # Since we are doing sliding, we need to join the datasets again of train and test
    X_w = np.concatenate((X_train, X_test))
    y_w = np.concatenate((y_train, y_test))

    X_w, y_w = window_data(X_w, y_w, window=WINDOW_LENGTH)
    X_train_w = X_w[:-len(X_test)]
    y_train_w = y_w[:-len(X_test)]
    X_test_w = X_w[-len(X_test):]
    y_test_w = y_w[-len(X_test):]

    # Check we will have same test set as in the previous models, make sure we didnt screw up on the windowing
    print(f"Test set equal: {np.array_equal(y_test_w,y_test)}")
	
    train_data = tf.data.Dataset.from_tensor_slices((X_train_w, y_train_w))
    train_data = train_data.cache().shuffle(BUFFER_SIZE).batch(BATCH_SIZE).repeat()

    val_data = tf.data.Dataset.from_tensor_slices((X_test_w, y_test_w))
    val_data = val_data.batch(BATCH_SIZE).repeat()
    return X_train_w, X_test_w, train_data, val_data, df_test

def train(X_train_w,train_data,val_data):
    dropout = 0.0
    simple_lstm_model = tf.keras.models.Sequential([
        tf.keras.layers.LSTM(
            128, input_shape=X_train_w.shape[-2:], dropout=dropout),
    	    tf.keras.layers.Dense(128),
    	    tf.keras.layers.Dense(128),
    	    tf.keras.layers.Dense(1)
    ])

    simple_lstm_model.compile(optimizer='rmsprop', loss='mae')
	
    EVALUATION_INTERVAL = 200
    EPOCHS = 5

    model_history = simple_lstm_model.fit(
            train_data, epochs=EPOCHS,
            steps_per_epoch=EVALUATION_INTERVAL,
            validation_data=val_data,
            validation_steps=50)  # ,callbacks=[tensorboard_callback]) #Uncomment this line for tensorboard support
    return simple_lstm_model

def predict(X_test_w, df_test, model):
    resultsDict = {}
    predictionsDict = {}
    yhat = model.predict(X_test_w).reshape(1, -1)[0]
    #resultsDict['Tensorflow simple LSTM'] = evaluate(y_test, yhat)
    predictionsDict['Tensorflow simple LSTM'] = yhat
    print(predictionsDict['Tensorflow simple LSTM'])

    yhat = pd.DataFrame(yhat)
    plt.plot(df_test.pollution_today.values, label='Original')
    print(yhat)
    plt.plot(yhat, color='red', label='LSTM')
    plt.legend()

def run():
    X_train_w, X_test_w, train_data, val_data, df_test = prepare_data()
    model = train(X_train_w, train_data, val_data)
    predict(X_test_w, df_test, model)

#if __name__ == '__main__':
@app.get("/predict")
async def main(background_tasks: BackgroundTasks):
    background_tasks.add_task(run)
    return {"value": 0}
