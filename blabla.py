!pip install backtrader optuna

import math
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sys
sys.path.insert(1, '/kaggle/input/marac1')

import tensorflow as tf
from tensorflow.keras.layers import MultiHeadAttention, Dense, Input, Dropout, BatchNormalization
import tensorflow.keras.backend as K
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from sklearn import preprocessing
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score
import time

# ------------------ Backtrader & Optuna ------------------
import backtrader as bt
import optuna
# ---------------------------------------------------------


import random
random.seed(42)
np.random.seed(42)
tf.random.set_seed(42)


tf.config.run_functions_eagerly(False)

physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    for k in range(len(physical_devices)):
        tf.config.experimental.set_memory_growth(physical_devices[k], True)
        print('memory growth:', tf.config.experimental.get_memory_growth(physical_devices[k]))
else:
    print("Not enough GPU hardware devices available")

# -------------------------------------------------------------------
#  HORIZON CONSTANTS (FIXED – not tuned by Optuna)
# -------------------------------------------------------------------
SRC_LEN = 12         # input sequence length (lookback)
TGT_LEN = 1           # forecast horizon
DEC_LEN = 1           # decoder input length (same as TGT_LEN in this setup)
MULPR_LEN = TGT_LEN   # step size for window creation
WINDOW_SIZE = SRC_LEN

# -------------------------------------------------------------------
#  Fixed parts of the model that depend on horizon
# -------------------------------------------------------------------
def positional_encoding(max_position, d_model):
    angle_rads = np.arange(max_position)[:, np.newaxis] / np.power(
        10000, (2 * (np.arange(d_model)[np.newaxis, :] // 2)) / d_model
    )
    angle_rads[:, 0::2] = np.sin(angle_rads[:, 0::2])
    angle_rads[:, 1::2] = np.cos(angle_rads[:, 1::2])
    return tf.cast(angle_rads[np.newaxis, ...], dtype=tf.float32)

def create_look_ahead_mask(tgt_len, src_len):
    mask1 = tf.linalg.band_part(tf.ones((tgt_len, tgt_len)), -1, 0)
    mask2 = tf.ones((tgt_len, src_len))
    mask_combined = tf.cast(mask1, tf.int32) & tf.cast(mask2, tf.int32)
    return tf.cast(mask_combined, dtype=tf.float32)[tf.newaxis, ...]

# -------------------------------------------------------------------
#  Data loading & preprocessing (same as original, but with fixed horizon)
# -------------------------------------------------------------------
l = ['000001.SS']

for i in l:
    filename = '/kaggle/input/datasets/marioprobst/xauusd07/work3.csv'
    df = pd.read_csv(filename, delimiter=',', parse_dates=['Date'],
                     usecols=['Date','Open','High','Low','Close','Volume'])
    df = df.sort_values('Date')
    division_rate1 = 0.6
    division_rate2 = 0.95

    def get_stock_data():
        df = pd.read_csv(filename)
        df.drop(['Date'], axis=1, inplace=True)
        close_series = df['Close']
        diff_series = close_series.diff(1).dropna()
        df = df.drop(0, axis=0)
        df['Close'] = diff_series
        df = df.reset_index(drop=True)
        return df, close_series.tolist(), diff_series.tolist()

    def load_data(df, seq_len, mul, normalize=True):
        amount_of_features = 1
        data = df.values
        row1 = round(division_rate1 * data.shape[0])
        row2 = round(division_rate2 * data.shape[0])
        train = data[:int(row1), :]
        valid = data[int(row1):int(row2), :]
        test = data[int(row2):, :]

        if normalize:
            train_close = train[:, -2].reshape(-1, 1)
            valid_close = valid[:, -2].reshape(-1, 1)
            test_close  = test[:, -2].reshape(-1, 1)

            standard_scaler = StandardScaler()
            train_close_scaled = standard_scaler.fit_transform(train_close)
            valid_close_scaled = standard_scaler.transform(valid_close)
            test_close_scaled  = standard_scaler.transform(test_close)
        else:
            train_close_scaled = train[:, -2].reshape(-1, 1)
            valid_close_scaled = valid[:, -2].reshape(-1, 1)
            test_close_scaled  = test[:, -2].reshape(-1, 1)
            standard_scaler = None

        train_close_scaled = train_close_scaled.ravel()
        valid_close_scaled = valid_close_scaled.ravel()
        test_close_scaled  = test_close_scaled.ravel()

        def create_windows(arr, samples):
            X, y = [], []
            for i in range(0, samples, mul):
                X.append(arr[i:i+seq_len])
                y.append(arr[i+seq_len:i+seq_len+TGT_LEN])
            return np.array(X), np.array(y)

        X_train, y_train = create_windows(train_close_scaled, train.shape[0] - seq_len - mul + 1)
        X_valid, y_valid = create_windows(valid_close_scaled, valid.shape[0] - seq_len - mul + 1)
        X_test,  y_test  = create_windows(test_close_scaled,  test.shape[0] - seq_len - mul + 1)

        X_train = X_train.reshape(-1, seq_len, amount_of_features)
        X_valid = X_valid.reshape(-1, seq_len, amount_of_features)
        X_test  = X_test.reshape(-1, seq_len, amount_of_features)

        return X_train, y_train, X_valid, y_valid, X_test, y_test, standard_scaler

    # Pre‑load data (horizon fixed, so this is done only once)
    df_diff, list_orig, list1_orig = get_stock_data()
    X_train, y_train, X_valid, y_valid, X_test, y_test, scaler = load_data(df_diff, SRC_LEN, MULPR_LEN)

    # -------------------------------------------------------------------
    #  Optuna‑tunable model building blocks
    # -------------------------------------------------------------------
    class FullyConnected(tf.keras.layers.Layer):
        def __init__(self, dense_dim, d_model, dropout_rate, batchnorm_momentum=0.98):
            super().__init__()
            self.dense1 = Dense(dense_dim, activation='relu',
                                kernel_initializer=tf.keras.initializers.HeNormal(),
                                bias_initializer=tf.keras.initializers.RandomUniform(minval=0.005, maxval=0.08))
            self.bn1 = BatchNormalization(momentum=batchnorm_momentum, epsilon=5e-4)
            self.dense2 = Dense(d_model,
                                kernel_initializer=tf.keras.initializers.HeNormal(),
                                bias_initializer=tf.keras.initializers.RandomUniform(minval=0.001, maxval=0.01))
            self.bn2 = BatchNormalization(momentum=batchnorm_momentum, epsilon=5e-4)
            self.dropout = Dropout(dropout_rate)

        def call(self, x, training=False):
            x = self.dense1(x)
            x = self.bn1(x, training=training)
            x = self.dense2(x)
            x = self.bn2(x, training=training)
            x = self.dropout(x, training=training)
            return x

    class EncoderLayer(tf.keras.layers.Layer):
        def __init__(self, num_heads, d_k, dropout_rate, dense_dim, d_model):
            super().__init__()
            self.mha = MultiHeadAttention(num_heads=num_heads, key_dim=d_k, dropout=dropout_rate,
                                          kernel_initializer=tf.keras.initializers.HeNormal(),
                                          kernel_regularizer=tf.keras.regularizers.L2(1e-4),
                                          bias_initializer=tf.keras.initializers.RandomUniform(minval=0.001, maxval=0.01))
            self.ffn = FullyConnected(dense_dim, d_model, dropout_rate)
            self.batchnorm1 = BatchNormalization(momentum=0.95, epsilon=1e-4)
            self.batchnorm2 = BatchNormalization(momentum=0.95, epsilon=1e-4)

        def call(self, x, training=False):
            attn_output = self.mha(query=x, value=x)
            out1 = self.batchnorm1(tf.add(x, attn_output), training=training)
            ffn_output = self.ffn(out1, training=training)
            out2 = self.batchnorm2(tf.add(ffn_output, out1), training=training)
            return out2

    class Encoder(tf.keras.layers.Layer):
        def __init__(self, num_layers, num_heads, d_model, d_k, dense_dim, dropout_rate):
            super().__init__()
            self.num_layers = num_layers
            self.lin_input = Dense(d_model, activation="relu")
            self.pos_encoding = positional_encoding(SRC_LEN, d_model)
            self.enc_layers = [
                EncoderLayer(num_heads, d_k, dropout_rate, dense_dim, d_model)
                for _ in range(num_layers)
            ]

        def call(self, x, training=False):
            x = self.lin_input(x)
            seq_len = tf.shape(x)[1]
            x += self.pos_encoding[:, :seq_len, :]
            for layer in self.enc_layers:
                x = layer(x, training=training)
            return x

    class DecoderLayer(tf.keras.layers.Layer):
        def __init__(self, num_heads, d_k, dropout_rate, dense_dim, d_model):
            super().__init__()
            self.mha1 = MultiHeadAttention(num_heads=num_heads, key_dim=d_k, dropout=dropout_rate,
                                           kernel_initializer=tf.keras.initializers.HeNormal(),
                                           kernel_regularizer=tf.keras.regularizers.L2(1e-4),
                                           bias_initializer=tf.keras.initializers.RandomUniform(minval=0.001, maxval=0.01))
            self.mha2 = MultiHeadAttention(num_heads=num_heads, key_dim=d_k, dropout=dropout_rate,
                                           kernel_initializer=tf.keras.initializers.HeNormal(),
                                           kernel_regularizer=tf.keras.regularizers.L2(1e-4),
                                           bias_initializer=tf.keras.initializers.RandomUniform(minval=0.001, maxval=0.01))
            self.ffn = FullyConnected(dense_dim, d_model, dropout_rate)
            self.batchnorm1 = BatchNormalization(momentum=0.95, epsilon=1e-4)
            self.batchnorm2 = BatchNormalization(momentum=0.95, epsilon=1e-4)
            self.batchnorm3 = BatchNormalization(momentum=0.95, epsilon=1e-4)

        def call(self, y, enc_output, dec_ahead_mask, enc_memory_mask, training=False):
            mult_attn_out1 = self.mha1(query=y, value=y, attention_mask=dec_ahead_mask)
            Q1 = self.batchnorm1(tf.add(y, mult_attn_out1), training=training)
            mult_attn_out2 = self.mha2(query=Q1, value=enc_output, key=enc_output, attention_mask=enc_memory_mask)
            mult_attn_out2 = self.batchnorm2(tf.add(mult_attn_out2, Q1), training=training)
            ffn_output = self.ffn(mult_attn_out2, training=training)
            out3 = self.batchnorm3(tf.add(ffn_output, mult_attn_out2), training=training)
            return out3

    class Decoder(tf.keras.layers.Layer):
        def __init__(self, num_layers, num_heads, d_model, d_k, dense_dim, dropout_rate):
            super().__init__()
            self.num_layers = num_layers
            self.lin_input = Dense(d_model, activation="relu")
            self.pos_encoding = positional_encoding(DEC_LEN, d_model)
            self.dec_layers = [
                DecoderLayer(num_heads, d_k, dropout_rate, dense_dim, d_model)
                for _ in range(num_layers)
            ]
            self.dec_ahead_mask = create_look_ahead_mask(DEC_LEN, DEC_LEN)
            self.enc_memory_mask = create_look_ahead_mask(DEC_LEN, SRC_LEN)

        def call(self, y, enc_output, training=False):
            y = self.lin_input(y)
            dec_len = tf.shape(y)[1]
            y += self.pos_encoding[:, :dec_len, :]
            for layer in self.dec_layers:
                y = layer(y, enc_output, self.dec_ahead_mask, self.enc_memory_mask, training=training)
            return y

    class Transformer(tf.keras.Model):
        def __init__(self, num_layers, num_heads, d_model, d_k, dense_dim, dropout_rate):
            super().__init__()
            self.encoder = Encoder(num_layers, num_heads, d_model, d_k, dense_dim, dropout_rate)
            self.decoder = Decoder(num_layers, num_heads, d_model, d_k, dense_dim, dropout_rate)
            self.linear_map = tf.keras.Sequential([
                Dense(dense_dim, activation="relu",
                      kernel_initializer=tf.keras.initializers.HeNormal(),
                      bias_initializer=tf.keras.initializers.RandomUniform(minval=0.001, maxval=0.02)),
                BatchNormalization(momentum=0.97, epsilon=5e-4),
                Dense(1)
            ])
            self.final_dense = Dense(TGT_LEN)

        def call(self, x, training=False):
            enc_input = x[:, :SRC_LEN, :]
            dec_input = x[:, -DEC_LEN:, :]
            enc_output = self.encoder(enc_input, training=training)
            dec_output = self.decoder(dec_input, enc_output, training=training)
            final_output = self.linear_map(dec_output, training=training)
            final_output = tf.transpose(final_output, perm=[0, 2, 1])
            final_output = self.final_dense(final_output)
            final_output = tf.transpose(final_output, perm=[0, 2, 1])
            return final_output

    # Custom loss (same as original)
    def up_down_accuracy(real, pre):
        mse = tf.reduce_mean(tf.square(pre - real))
        accu = tf.multiply(real, pre)
        accu = tf.nn.relu(accu)
        accu = tf.sign(accu)
        accu = tf.reduce_mean(accu)
        accu = 1 - accu
        safe_mse = tf.abs(mse) + 1e-7
        log10_mse = tf.math.log(safe_mse) / tf.math.log(10.0)
        floor_log10 = tf.floor(log10_mse)
        loss = accu * tf.pow(10.0, floor_log10) + mse
        return loss

    # -------------------------------------------------------------------
    #  OPTUNA OBJECTIVE FUNCTION
    # -------------------------------------------------------------------
   # -------------------------------------------------------------------
#  OPTUNA OBJECTIVE WITH TUNABLE src_len
# -------------------------------------------------------------------
    def objective(trial):
        tf.keras.backend.clear_session()
    
        # ----- Suggest horizon -----
        src_len = 12  # you can change range/step
    
        # ----- Suggest other hyperparameters -----
        d_model = trial.suggest_categorical('d_model', [8, 16, 32, 64])
        num_heads = trial.suggest_categorical('num_heads', [2, 4, 8])
        # Ensure divisibility
        while d_model % num_heads != 0:
            d_model = trial.suggest_categorical('d_model', [8, 16, 32, 64])
        d_k = d_model // num_heads
    
        dense_dim = trial.suggest_categorical('dense_dim', [16, 32, 64])
        num_layers = trial.suggest_int('num_layers', 1, 3)
        dropout_rate = trial.suggest_float('dropout_rate', 0.1, 0.4)
        learning_rate = trial.suggest_float('learning_rate', 1e-5, 1e-2, log=True)
        batch_size = trial.suggest_categorical('batch_size', [128, 256, 512])
        epochs = trial.suggest_int('epochs', 20, 60)
    
        # ----- Load data with this src_len -----
        # Use the same df_diff (global) and re‑window
        X_train, y_train, X_valid, y_valid, _, _, _ = load_data(
            df_diff, src_len, mul=TGT_LEN, normalize=True
        )
        # Note: load_data returns scaler too, but we don't need it for validation loss
    
        # ----- Build model dynamically -----
        class DynamicFullyConnected(tf.keras.layers.Layer):
            def __init__(self, dense_dim, d_model, dropout_rate):
                super().__init__()
                self.dense1 = Dense(dense_dim, activation='relu',
                                    kernel_initializer='he_normal')
                self.bn1 = BatchNormalization(momentum=0.98, epsilon=5e-4)
                self.dense2 = Dense(d_model, kernel_initializer='he_normal')
                self.bn2 = BatchNormalization(momentum=0.98, epsilon=5e-4)
                self.dropout = Dropout(dropout_rate)
            def call(self, x, training=False):
                x = self.dense1(x)
                x = self.bn1(x, training=training)
                x = self.dense2(x)
                x = self.bn2(x, training=training)
                return self.dropout(x, training=training)
    
        class DynamicEncoderLayer(tf.keras.layers.Layer):
            def __init__(self, num_heads, d_k, dropout_rate, dense_dim, d_model):
                super().__init__()
                self.mha = MultiHeadAttention(num_heads=num_heads, key_dim=d_k,
                                              dropout=dropout_rate,
                                              kernel_regularizer=tf.keras.regularizers.L2(1e-4))
                self.ffn = DynamicFullyConnected(dense_dim, d_model, dropout_rate)
                self.bn1 = BatchNormalization(momentum=0.95, epsilon=1e-4)
                self.bn2 = BatchNormalization(momentum=0.95, epsilon=1e-4)
            def call(self, x, training=False):
                attn = self.mha(query=x, value=x)
                x = self.bn1(x + attn, training=training)
                ffn_out = self.ffn(x, training=training)
                return self.bn2(x + ffn_out, training=training)
    
        class DynamicEncoder(tf.keras.layers.Layer):
            def __init__(self, num_layers, num_heads, d_model, d_k, dense_dim,
                         dropout_rate, src_len):
                super().__init__()
                self.src_len = src_len
                self.lin = Dense(d_model, activation='relu')
                self.pos_enc = positional_encoding(src_len, d_model)
                self.layers = [DynamicEncoderLayer(num_heads, d_k, dropout_rate,
                                                   dense_dim, d_model)
                               for _ in range(num_layers)]
            def call(self, x, training=False):
                x = self.lin(x)
                seq_len = tf.shape(x)[1]
                x += self.pos_enc[:, :seq_len, :]
                for layer in self.layers:
                    x = layer(x, training=training)
                return x
    
        class DynamicDecoderLayer(tf.keras.layers.Layer):
            def __init__(self, num_heads, d_k, dropout_rate, dense_dim, d_model):
                super().__init__()
                self.mha1 = MultiHeadAttention(num_heads=num_heads, key_dim=d_k,
                                               dropout=dropout_rate,
                                               kernel_regularizer=tf.keras.regularizers.L2(1e-4))
                self.mha2 = MultiHeadAttention(num_heads=num_heads, key_dim=d_k,
                                               dropout=dropout_rate,
                                               kernel_regularizer=tf.keras.regularizers.L2(1e-4))
                self.ffn = DynamicFullyConnected(dense_dim, d_model, dropout_rate)
                self.bn1 = BatchNormalization(momentum=0.95, epsilon=1e-4)
                self.bn2 = BatchNormalization(momentum=0.95, epsilon=1e-4)
                self.bn3 = BatchNormalization(momentum=0.95, epsilon=1e-4)
            def call(self, y, enc_out, mask1, mask2, training=False):
                attn1 = self.mha1(query=y, value=y, attention_mask=mask1)
                y = self.bn1(y + attn1, training=training)
                attn2 = self.mha2(query=y, value=enc_out, key=enc_out,
                                  attention_mask=mask2)
                y = self.bn2(y + attn2, training=training)
                ffn_out = self.ffn(y, training=training)
                return self.bn3(y + ffn_out, training=training)
    
        class DynamicDecoder(tf.keras.layers.Layer):
            def __init__(self, num_layers, num_heads, d_model, d_k, dense_dim,
                         dropout_rate, src_len, dec_len=1):
                super().__init__()
                self.dec_len = dec_len
                self.lin = Dense(d_model, activation='relu')
                self.pos_enc = positional_encoding(dec_len, d_model)
                self.layers = [DynamicDecoderLayer(num_heads, d_k, dropout_rate,
                                                   dense_dim, d_model)
                               for _ in range(num_layers)]
                self.mask1 = create_look_ahead_mask(dec_len, dec_len)
                self.mask2 = create_look_ahead_mask(dec_len, src_len)
    
            def call(self, y, enc_out, training=False):
                y = self.lin(y)
                seq_len = tf.shape(y)[1]
                y += self.pos_enc[:, :seq_len, :]
                for layer in self.layers:
                    y = layer(y, enc_out, self.mask1, self.mask2, training=training)
                return y
    
        class DynamicTransformer(tf.keras.Model):
            def __init__(self, num_layers, num_heads, d_model, d_k, dense_dim,
                         dropout_rate, src_len, dec_len=1, tgt_len=1):
                super().__init__()
                self.src_len = src_len
                self.dec_len = dec_len
                self.tgt_len = tgt_len
                self.encoder = DynamicEncoder(num_layers, num_heads, d_model, d_k,
                                              dense_dim, dropout_rate, src_len)
                self.decoder = DynamicDecoder(num_layers, num_heads, d_model, d_k,
                                              dense_dim, dropout_rate, src_len, dec_len)
                self.linear_map = tf.keras.Sequential([
                    Dense(dense_dim, activation='relu'),
                    BatchNormalization(momentum=0.97, epsilon=5e-4),
                    Dense(1)
                ])
                self.final_dense = Dense(tgt_len)
    
            def call(self, x, training=False):
                enc_in = x[:, :self.src_len, :]
                dec_in = x[:, -self.dec_len:, :]
                enc_out = self.encoder(enc_in, training=training)
                dec_out = self.decoder(dec_in, enc_out, training=training)
                out = self.linear_map(dec_out, training=training)
                out = tf.transpose(out, [0, 2, 1])
                out = self.final_dense(out)
                out = tf.transpose(out, [0, 2, 1])
                return out
    
        model = DynamicTransformer(
            num_layers=num_layers,
            num_heads=num_heads,
            d_model=d_model,
            d_k=d_k,
            dense_dim=dense_dim,
            dropout_rate=dropout_rate,
            src_len=src_len,
            dec_len=1,
            tgt_len=1
        )
        # Build
        dummy = tf.random.normal((1, src_len + 1, 1))   # src + dec
        _ = model(dummy)
    
        model.compile(
            loss=up_down_accuracy,
            optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
            metrics=[up_down_accuracy]
        )
    
        early_stop = EarlyStopping(monitor='val_loss', patience=10,
                                   restore_best_weights=True)
    
        history = model.fit(
            X_train, y_train,
            validation_data=(X_valid, y_valid),
            epochs=epochs,
            batch_size=batch_size,
            callbacks=[early_stop],
            verbose=1
        )
    
        return min(history.history['val_loss'])

    # -------------------------------------------------------------------
    #  RUN OPTUNA STUDY
    # -------------------------------------------------------------------
    print("Starting Optuna hyperparameter optimization...")
    study = optuna.create_study(direction='minimize',
                                sampler=optuna.samplers.TPESampler(seed=42),
                                pruner=optuna.pruners.MedianPruner(n_startup_trials=5))
    study.optimize(objective, n_trials=1, timeout=7200)  # adjust trials/time as needed

    print("Best trial:")
    best_trial = study.best_trial
    print(f"  Value (val_loss): {best_trial.value}")
    print("  Params:")
    for key, value in best_trial.params.items():
        print(f"    {key}: {value}")

    # -------------------------------------------------------------------
    #  RETRAIN FINAL MODEL ON TRAIN+VAL WITH BEST HYPERPARAMETERS
    # -------------------------------------------------------------------
    # Combine train and validation for final training (optional)
    X_train_final = np.concatenate([X_train, X_valid], axis=0)
    y_train_final = np.concatenate([y_train, y_valid], axis=0)

    tf.keras.backend.clear_session()

    # Retrieve best hyperparameters
    bp = best_trial.params
    d_model = bp['d_model']
    num_heads = bp['num_heads']
    d_k = d_model // num_heads
    dense_dim = bp['dense_dim']
    num_layers = bp['num_layers']
    dropout_rate = bp['dropout_rate']
    learning_rate = bp['learning_rate']
    batch_size = bp['batch_size']
    epochs_final = bp['epochs']
    src_len = bp['src_len'] # you might want to train longer now

    X_train_best, y_train_best, X_valid_best, y_valid_best, X_test_best, y_test_best, scaler = load_data(
        df_diff, src_len, mul=TGT_LEN, normalize=True
    )

    model_final = Transformer(
        num_layers=num_layers,
        num_heads=num_heads,
        d_model=d_model,
        d_k=d_k,
        dense_dim=dense_dim,
        dropout_rate=dropout_rate
    )
    dummy_input = tf.random.normal((1, src_len + DEC_LEN, 1))
    _ = model_final(dummy_input, training=False)

    model_final.compile(
        loss=up_down_accuracy,
        optimizer=tf.keras.optimizers.Adam(learning_rate=learning_rate),
        metrics=[up_down_accuracy]
    )

    print("\nTraining final model on train+validation set ...")
    model_final.fit(
        X_train_final, y_train_final,
        epochs=epochs_final,
        batch_size=batch_size,
        verbose=1
    )

    print("Final model training completed.\n")

    # -------------------------------------------------------------------
    #  BACKTRADER BACKTEST (UNCHANGED)
    # -------------------------------------------------------------------
    import datetime
    from backtrader import Order

    class TransformerStrategy(bt.Strategy):
        params = (
            ('src_len', SRC_LEN),
            ('risk_pct', 0.01),
            ('risk_reward_ratio', 4),
            ('test_start_date', None),
            ('max_hold_hours', 1),
        )

        def __init__(self, model=None, scaler=None):
            self.model = model
            self.scaler = scaler
            self.close_history = []
            self.test_start = self.p.test_start_date
            self.predictions_log = []
            self.last_prediction = None
            self.entry_dt = None
            self.bracket_orders = []

        def next(self):
            if self.position and self.entry_dt is not None:
                current_dt = self.data.datetime.datetime(0)
                elapsed = (current_dt - self.entry_dt).total_seconds() / 3600.0
                if elapsed >= self.p.max_hold_hours:
                    for order in self.bracket_orders:
                        if order and order.status in [Order.Submitted, Order.Accepted]:
                            self.cancel(order)
                    self.bracket_orders.clear()
                    self.close()
                    print(f'*** TIME EXIT {current_dt.date()} after {elapsed:.2f} hours ***')
                    self.entry_dt = None
                    return

            self.close_history.append(self.data.close[0])
            if len(self.close_history) < self.p.src_len + 1:
                return
            self.close_history = self.close_history[-(self.p.src_len + 1):]

            if self.last_prediction is not None:
                actual_change = self.data.close[0] - self.last_prediction['close']
                if actual_change > 1e-9:
                    actual_direction = 1
                elif actual_change < -1e-9:
                    actual_direction = -1
                else:
                    actual_direction = 0
                self.last_prediction['actual_direction'] = actual_direction
                self.predictions_log.append(self.last_prediction)
                self.last_prediction = None

            if self.data.datetime.date(0) < self.test_start:
                return

            closes = np.array(self.close_history)
            diff = np.diff(closes)
            diff_scaled = self.scaler.transform(diff.reshape(-1, 1))
            X = diff_scaled.reshape(1, self.p.src_len, 1)
            pred = self.model.predict(X, verbose=0)[0, 0, 0]
            pred_diff = self.scaler.inverse_transform([[pred]])[0, 0]
            direction = 1 if pred_diff > 0 else -1
            confidence = abs(pred_diff)

            self.last_prediction = {
                'datetime': self.data.datetime.date(0),
                'pred_direction': direction,
                'confidence': confidence,
                'close': self.data.close[0],
            }

            if not self.position:
                risk_amount = self.data.close[0] * self.p.risk_pct
                if direction == 1:
                    entry_price = self.data.close[0]
                    sl = entry_price - risk_amount
                    tp = entry_price + risk_amount * self.p.risk_reward_ratio
                    orders = self.buy_bracket(price=entry_price, stopprice=sl, limitprice=tp)
                else:
                    entry_price = self.data.close[0]
                    sl = entry_price + risk_amount
                    tp = entry_price - risk_amount * self.p.risk_reward_ratio
                    orders = self.sell_bracket(price=entry_price, stopprice=sl, limitprice=tp)

                self.bracket_orders = list(orders)
                self.entry_dt = self.data.datetime.datetime(0)

        def notify_order(self, order):
            if order.status in [order.Completed]:
                action = 'BUY' if order.isbuy() else 'SELL'
                print(f'{action}  {self.data.datetime.date(0)} @ {order.executed.price:.5f}')
            elif order.status == order.Rejected:
                print(f'ORDER REJECTED – reason possible: {order.Rejected}')
            elif order.status == order.Margin:
                print('ORDER REJECTED – insufficient margin')

        def notify_trade(self, trade):
            if trade.isclosed:
                print(f'TRADE CLOSED {self.data.datetime.date(0)} PNL: {trade.pnl:.2f}')

    # Set up Backtrader
    test_start_index = round(division_rate2 * len(df))
    test_start_date = df['Date'].iloc[test_start_index].date()

    data_feed = bt.feeds.PandasData(
        dataname=df.set_index('Date'),
        open='Open', high='High', low='Low', close='Close', volume='Volume'
    )

    cerebro = bt.Cerebro()
    cerebro.adddata(data_feed)



    cerebro.addstrategy(
    TransformerStrategy,
    test_start_date=test_start_date,
    model=model_final,
    scaler=scaler,
    src_len=src_len           # this will override the default param
    )

    cerebro.broker.setcash(10000.0)
    cerebro.broker.setcommission(commission=0.00002)
    cerebro.addsizer(bt.sizers.FixedSize, stake=1)
    cerebro.addanalyzer(bt.analyzers.DrawDown, _name='drawdown')

    print(f"Starting Portfolio Value: {cerebro.broker.getvalue():.2f}")
    cerebro.run()



    strat = cerebro.runstrats[0][0]
    # 3. Extract and print the Max Drawdown
    drawdown_info = strat.analyzers.drawdown.get_analysis()
    max_drawdown = drawdown_info.max.drawdown
    print(f"Max Drawdown: {max_drawdown:.2f}%")
    log = strat.predictions_log
    df_log = pd.DataFrame(log)
    df_log['correct'] = (df_log['pred_direction'] == df_log['actual_direction']).astype(int)
    accuracy = df_log['correct'].mean()
    print(f"Overall direction accuracy: {accuracy:.2%}")

    # Binned accuracy by confidence
    df_log['conf_bin'] = pd.qcut(df_log['confidence'], q=5, duplicates='drop')
    accuracy_by_bin = df_log.groupby('conf_bin')['correct'].mean()
    print("\nAccuracy per confidence bin:")
    print(accuracy_by_bin)

    bin_centers = [iv.mid for iv in accuracy_by_bin.index]
    plt.figure(figsize=(8,4))
    plt.plot(bin_centers, accuracy_by_bin.values, marker='o')
    plt.xlabel('Confidence (abs predicted change, $)')
    plt.ylabel('Direction Accuracy')
    plt.title('Model Calibration: Accuracy vs Confidence')
    plt.grid(True)
    plt.show()

    print(f"Final Portfolio Value: {cerebro.broker.getvalue():.2f}")
    cerebro.plot()

    print("teststart date", test_start_date)