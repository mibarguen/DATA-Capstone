from utils import *
from datagen.spectra_loader import SpectraLoader
import json
from sklearn.preprocessing import OneHotEncoder
import numpy as np
import random


class SpectraPreprocessor:

    def __init__(self, dataset_name, num_channels, num_instances, use_generator=False):
        self.train_spectra_loader = SpectraLoader(dataset_name=dataset_name, subset_prefix=TRAIN_DATASET_PREFIX, eval_now=not use_generator)
        self.test_spectra_loader = SpectraLoader(dataset_name=dataset_name, subset_prefix=TEST_DATASET_PREFIX)
        self.one_hot_encoder = OneHotEncoder(sparse=False, categories='auto')
        self.datagen_config = json.load(open(os.path.join(DATA_DIR, dataset_name, DATAGEN_CONFIG), "r"))
        self.max_nc = self.datagen_config['num_channels']
        self.num_channels = num_channels
        self.num_instances = num_instances

        # TODO: Fix this.
        _, y_test = self.get_data(self.test_spectra_loader)
        self.one_hot_encoder.fit(y_test)

    def get_data(self, loader):
        dm = loader.get_dm()
        dm_reshaped = np.array(dm[:self.num_instances])[:, :self.num_channels, :]
        # TODO: Correct?
        X = dm_reshaped.reshape(dm_reshaped.shape[0], dm_reshaped.shape[2], dm_reshaped.shape[1])
        # Subset X.
        # TODO: Check if sufficient number of channels.
        #X_reshaped = X[:self.num_instances, :, :self.num_channels]
        y = np.array(loader.get_n())
        y = y.reshape(y.shape[0], 1)
        y_reshaped = y[:self.num_instances, :]
        del y, dm
        return X, y_reshaped

    def pad_channels(self, X, additional_nc, mode='symmetric'):
        return np.pad(X, ((0, 0), (0, 0), (0, additional_nc)), mode)

    def transform(self, pad_nc=None, encoded=False):
        X_train, y_train = self.transform_train(encoded=encoded)
        X_test, y_test = self.transform_test(encoded=encoded)
        if pad_nc is not None:
            X_train = self.pad_channels(X_train, pad_nc - self.num_channels)
            X_test = self.pad_channels(X_test, pad_nc - self.num_channels)
        return X_train, y_train, X_test, y_test

    def transform_train(self, encoded=False):
        X_train, y_train = self.get_data(self.train_spectra_loader)
        self.one_hot_encoder.fit(y_train)
        if encoded:
            y_train = self.one_hot_encoder.transform(y_train)
        return X_train, y_train

    def transform_test(self, encoded=False):
        X_test, y_test = self.get_data(self.test_spectra_loader)
        if encoded:
            y_test = self.one_hot_encoder.transform(y_test)
        return X_test, y_test

    def train_generator(self, batch_size, encoded=False):
        cur_set_i = 0
        files = self.train_spectra_loader.get_data_files()

        num_files = len(files)
        spectra_x = None
        spectra_y = None

        while True:
            if cur_set_i >= num_files:
                cur_set_i = 0
                random.shuffle(files)

            self.train_spectra_loader.load_spectra([files[cur_set_i]], del_old=True)
            cur_set_i += 1
            dat = self.transform_train(encoded=encoded)

            if spectra_x is None:
                spectra_x = dat[0]
            else:
                spectra_x = np.concatenate((spectra_x, dat[0]))

            if spectra_y is None:
                spectra_y = dat[1]
            else:
                spectra_y = np.concatenate((spectra_y, dat[1]))

            while len(spectra_x) >= batch_size:
                spectra_batch_x = spectra_x[:batch_size]
                spectra_batch_y = spectra_y[:batch_size]
                spectra_x = spectra_x[batch_size:]
                spectra_y = spectra_y[batch_size:]
                
                yield spectra_batch_x, spectra_batch_y

    def get_num_training_files(self):
        return len(self.train_spectra_loader.get_data_files())
