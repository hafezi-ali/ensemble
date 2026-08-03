
import time
import sys
import seaborn as sns
import plotly.express as px
import re
from collections import Counter
from datetime import date
from datetime import time
from datetime import timedelta
from datetime import datetime
# from imblearn.over_sampling import BorderlineSMOTE
# from imblearn.over_sampling import SMOTENC
from os import chdir as cd
import numpy as np
from numpy import mean
from numpy import std
from numpy import argmax
import warnings

# Predictive libs
from sklearn.metrics import average_precision_score, accuracy_score ,recall_score, f1_score
from sklearn.metrics import roc_curve, auc,precision_recall_fscore_support, average_precision_score
from sklearn.metrics import precision_recall_curve, auc, confusion_matrix,accuracy_score
from tensorflow.keras.metrics import AUC, Precision, Recall
from sklearn.svm import SVC
from sklearn import tree
from sklearn.model_selection import cross_val_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn import metrics
# from pretty_confusion_matrix import pp_matrix_from_data

import pandas as pd
import tensorflow as tf

import sklearn
from sklearn.preprocessing import scale, MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from pandas import read_csv
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from sklearn.preprocessing import MinMaxScaler
from sklearn import preprocessing

from sklearn.metrics import f1_score, precision_score, recall_score, confusion_matrix
import itertools
# from imblearn.over_sampling import RandomOverSampler
from matplotlib import pyplot as plt

from sklearn.model_selection import GridSearchCV
import math

from collections import Counter
from sklearn.decomposition import PCA
from sklearn.metrics import classification_report, confusion_matrix
from tensorflow import keras
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.callbacks import ModelCheckpoint, EarlyStopping
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.layers import Dropout

# from tensorflow.keras.wrappers.scikit_learn import KerasClassifier
# from scikeras.wrappers import KerasClassifier

from tensorflow.keras.constraints import MaxNorm as maxnorm
from tensorflow.keras import regularizers
from tensorflow.keras.layers import Conv1D
from tensorflow.keras.layers import MaxPooling1D

from sklearn.model_selection import RepeatedKFold
from sklearn.model_selection import KFold

from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from matplotlib import pyplot
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_predict


from sklearn.datasets import make_classification
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.model_selection import StratifiedKFold

from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn import svm
from sklearn.naive_bayes import GaussianNB
from matplotlib import pyplot
import time
from os import chdir as cd
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import StandardScaler
# import umap.umap_ as umap

from sklearn.model_selection import cross_val_score
from sklearn.datasets import load_iris
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import BaggingClassifier
import plotly.express as px
import plotly.io as pio
from sklearn.cluster import KMeans
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import StackingClassifier
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import SGDClassifier

from statsmodels.graphics.gofplots import qqplot
from sklearn.manifold import TSNE
from sklearn.cluster import DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.model_selection import cross_validate
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, \
    roc_auc_score, cohen_kappa_score, balanced_accuracy_score
from numpy import linalg as LA

from scipy.spatial.distance import mahalanobis
import copy
from tqdm import tqdm
# MOE

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split, ParameterGrid
from sklearn.preprocessing import LabelEncoder
from torch.utils.data import TensorDataset, DataLoader, Dataset
import pprint
import time
from sklearn.model_selection import StratifiedKFold
from sklearn.preprocessing import MinMaxScaler
import pickle
import pandas as pd
from sklearn.model_selection import RepeatedKFold

from sklearn.base import clone
from scipy.stats import pearsonr
from sklearn.utils.validation import check_is_fitted
import warnings
from sklearn.exceptions import ConvergenceWarning
from functools import reduce

import math
import matplotlib.pyplot as plt
import pandas as pd

# import plotly.plotly as py
from mpl_toolkits.mplot3d import Axes3D
from scipy.stats import multivariate_normal
from plotly.figure_factory import create_distplot, create_2d_density, create_facet_grid
from plotly.offline import iplot


from joblib import Parallel, delayed
import pickle

