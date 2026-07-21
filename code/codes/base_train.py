# %%

import copy
# Import necessary libs
import os
import pickle

os.chdir('/content/drive/MyDrive/Thp')
# Set the PYTHONPATH environment variable to include the directory containing your modules
os.environ['PYTHONPATH'] = '/content/drive/MyDrive/Thp'

from Funcs.Functions import *
from Funcs.Model_functions import *
import Funcs
from Lib.lib import *
# %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Preprocessing %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

uci_data_handle_new = pd.read_csv('Data/UCI_HAR_Dataset/data_uci_handled.csv', index_col=0)
uci_data_handle_new['Activity'] = uci_data_handle_new['Activity'] + 1
database = {'uci': uci_data_handle_new}
# %%

X = database['uci'].drop(['Activity', 'ActivityName', 'subject'], axis=1)
y = database['uci']['ActivityName']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
# %%

# Normalization, Transformation, data_loaders
n_components = 'auto'
random_state_pca = None
random_state_moe_dist_split = None
single_preprocessing_res_grid = Funcs.Functions.single_preprocessing(X_train=X_train, X_test=X_test,
                                                                     y_train=y_train,
                                                                     n_components=n_components,
                                                                     random_state_pca=random_state_pca,
                                                                     # val_size=val_size,
                                                                     # val_batch_size=val_batch_size,
                                                                     # train_batch_size=train_batch_size,
                                                                     )
# %%

with open('Results/single_preprocessing_res_grid_main.pkl', 'wb') as f:
    pickle.dump(single_preprocessing_res_grid, f)
# %%

# main
# clustering on data
phi_list = np.arange(0.1, 1, 0.1)
n_c_list = np.arange(2, 7)
# phi = 0.4
random_state_clustering = None
random_state_cluster_samples_shuffling = 42
distance_metrics = 'Euclidean'
gmm = GaussianMixture()

def resampling_grid(phi_list, n_c_list, random_state_clustering, single_preprocessing_res_grid, y_train, distance_metrics):
    df_single_resampling_res_grid = pd.DataFrame(columns=['phi', 'n_c', 'single_resampling_res'])
    for phi in tqdm(phi_list, position=0, leave=True, desc="Phi Loop"):
        for n_c in tqdm(n_c_list, position=1, leave=True, desc="N_c Loop"):
            gmm_params = {
                'n_components': n_c,
                'random_state': random_state_clustering,
            }
            clusterig_method = gmm.set_params(**gmm_params)
            single_resampling_res = resampling(
                clusterig_method=clusterig_method,
                X_train_dist=single_preprocessing_res_grid['X_train'],
                y_train_dist=y_train, phi=phi,
                random_state_cluster_samples_shuffling=random_state_cluster_samples_shuffling,
                distance_metrics=distance_metrics)
            # df_single_resampling_res_grid = df_single_resampling_res_grid.append({'phi': phi, 'n_c': n_c,
            #                                       'single_resampling_res': single_resampling_res}, ignore_index=True)
            #
            new_row = pd.DataFrame({'phi': [phi], 'n_c': [n_c], 'single_resampling_res': [single_resampling_res]})
            df_single_resampling_res_grid = pd.concat([df_single_resampling_res_grid, new_row], ignore_index=True)
    return df_single_resampling_res_grid
# %%

df_single_resampling_res_grid = resampling_grid(phi_list, n_c_list, random_state_clustering,
                                             single_preprocessing_res_grid, y_train, distance_metrics)
# %%

with open('Results/df_single_resampling_res_grid_main', 'wb') as f:
    pickle.dump(df_single_resampling_res_grid, f)
# %%

models = get_models()
normalization = False
param_models_list = list()
model_param_grids = {
    'svm': {
        'C': [0.1, 1, 10, 100],
        'kernel': ['linear', 'poly', 'rbf', 'sigmoid'],
        'gamma': ['scale', 'auto']
    },
    'sgd': {
        'alpha': [0.0001, 0.001, 0.01],
        'loss': ['log_loss']
    },
    'lr': {
        'C': [0.1, 1, 10],
        'solver': ['lbfgs', 'liblinear','saga'],
    },
    'knn': {
        'n_neighbors': [3, 5, 7, 9],
        'weights': ['uniform', 'distance'],
        'algorithm': ['auto', 'ball_tree', 'kd_tree'],
    },
    'dt': {
        'criterion': ['gini', 'entropy'],
        'splitter': ['best', 'random'],
        'max_depth': [None, 10, 20, 30, 40, 50],
        'min_samples_split': [2, 10, 20],
        'min_samples_leaf': [1, 5, 10],
    }
}

# Use tqdm for iterrows
for index, row in tqdm(df_single_resampling_res_grid.iterrows(), total=len(df_single_resampling_res_grid), 
                       position=0, leave=True, desc="Grid Training"):
# for index, row in df_single_resampling_res_grid.iterrows():
    param_models = grid_train_base_models(
        cluster_samples=row['single_resampling_res']['rm_cluster_samples'],
        cluster_samples_lables=row['single_resampling_res']['rm_cluster_samples_labels'],
        model_param_grids=model_param_grids, models=models,
        normalization=normalization)
    param_models_list.append(param_models)
# %%
# new

df_single_resampling_res_grid['param_models_list'] = param_models_list
# %%

models = get_models()
models.pop('gn')
# %%

# models = {'svm': get_models()['svm']}
candidate_models_cluster_grid_nested = list()
for index, row in df_single_resampling_res_grid.iterrows():
    n_c = row['n_c']
    candidate_models_cluster_grid = list()
    for n_c in range(n_c):
        candidate_best_models = dict()
        for model in models:
            candidate_best_models[model] = {
                'best_params': row['param_models_list'][n_c][model][
                    'grid_' + model + '_cluster'].best_params_,
                'best_score_': row['param_models_list'][n_c][model][
                    'grid_' + model + '_cluster'].best_score_}
        candidate_models_cluster_grid.append(candidate_best_models)
    candidate_models_cluster_grid_nested.append(candidate_models_cluster_grid)
# %%

df_single_resampling_res_grid['candidate_models_cluster_grid'] = candidate_models_cluster_grid_nested
# %%

rm_duplicated_cv_results_model_sorteds_nested = list()
cv_results_model_sorteds_nested = list()
for index, row in df_single_resampling_res_grid.iterrows():
    n_c = row['n_c']
    cv_results_model_list = list()
    cv_results_model_sorted_list = list()
    rm_duplicated_cv_results_model_sorted_list = list()
    for i in range(n_c):
        cv_results_models_sorted = dict()
        rm_duplicated_cv_results_models_sorted = dict()
        for model in models:
            cv_results_model = pd.DataFrame(row['param_models_list'][i][model]['grid_' + model + '_cluster'].cv_results_)
            # Sort the dataframe by the mean test score in descending order
            cv_results_model_sorted = cv_results_model.sort_values(by='mean_test_score', ascending=False)
            rm_duplicated_cv_results_model_sorted = cv_results_model_sorted.drop_duplicates(subset=["mean_test_score"],
                                                                                        keep="first")
            cv_results_models_sorted[model] = cv_results_model_sorted
            rm_duplicated_cv_results_models_sorted[model] = rm_duplicated_cv_results_model_sorted

        # cv_results_model_list.append(cv_results_model)
        cv_results_model_sorted_list.append(cv_results_models_sorted)
        rm_duplicated_cv_results_model_sorted_list.append(rm_duplicated_cv_results_models_sorted)
    rm_duplicated_cv_results_model_sorteds_nested.append(rm_duplicated_cv_results_model_sorted_list)
    cv_results_model_sorteds_nested.append(cv_results_model_sorted_list)
# %%

df_single_resampling_res_grid['cv_results_model_sorteds'] = cv_results_model_sorteds_nested
df_single_resampling_res_grid['rm_duplicated_cv_results_model_sorteds'] = rm_duplicated_cv_results_model_sorteds_nested
# %%
# new_2

i = 0
best_models_clusters_nested = list()
sorted_candidate_models_cluster_grid_nested = list()
for row in cv_results_model_sorteds_nested:
    n_c = df_single_resampling_res_grid.iloc[i]['n_c']
    best_models_clusters_dict = dict()
    for model in models:
        best_models_clusters = [
            copy.deepcopy(models[model]).set_params(**row[i][model].iloc[:5]['params'].iloc[0])
            for i in range(n_c)]

        # best_models_clusters = [best_models_clusters[i].set_params(class_weight='balanced') for i in range(n_c)]
        best_models_clusters_dict[model] = best_models_clusters
    sorted_candidate_models_cluster_grid = sort_by_score(
        df_single_resampling_res_grid['candidate_models_cluster_grid'][i])
    sorted_candidate_models_cluster_grid_nested.append(sorted_candidate_models_cluster_grid)
    best_models_clusters_nested.append(best_models_clusters_dict)
    i+=1
# %%

df_single_resampling_res_grid['best_models_clusters'] = best_models_clusters_nested
df_single_resampling_res_grid['sorted_candidate_models_cluster_grid'] = sorted_candidate_models_cluster_grid_nested
# %%

with open('Results/df_single_resampling_res_grid_main_full.pkl', 'wb') as f:
    pickle.dump(df_single_resampling_res_grid, f)
# %%
#  #################################### end preprocessing ################################
