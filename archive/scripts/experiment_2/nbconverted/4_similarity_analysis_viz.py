#!/usr/bin/env python
# coding: utf-8

# # Similarity analysis
# 
# We want to determine if the different batch simulated data is able to capture the biological signal that is present in the original data:  How much of the real input data is captured in the simulated batch data?
# 
# In other words, we want to ask: “do these datasets have similar patterns”?
# 
# To do this we will use a visual inspection using PCA
# 
# **Approach:**
# 1. Given Dataset A = simulated data with everything in 1 batch and Dataset B = simulated data with X batches, where X = 1,2,3,....
# 2. Plot PC1 vs PC2 of combined dataset A + B
# 3. Color samples by whether they are from A or B
# 4. Visually inspect the overlap between A and B

# In[1]:


get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')

import os
import ast
import pandas as pd
import numpy as np
import random
import glob
from plotnine import *
from sklearn.decomposition import PCA
import warnings
warnings.filterwarnings(action='ignore')


# In[2]:


# Load config file
config_file = "config_exp_2.txt"

d = {}
float_params = ["learning_rate", "kappa", "epsilon_std"]
str_params = ["analysis_name", "NN_architecture"]
lst_params = ["num_batches"]
with open(config_file) as f:
    for line in f:
        (name, val) = line.split()
        if name in float_params:
            d[name] = float(val)
        elif name in str_params:
            d[name] = str(val)
        elif name in lst_params:
            d[name] = ast.literal_eval(val)
        else:
            d[name] = int(val)


# In[3]:


# Parameters
analysis_name = d["analysis_name"]
NN_architecture = d["NN_architecture"]
num_batches = d["num_batches"]


# In[4]:


# Load data
base_dir = os.path.abspath(os.path.join(os.getcwd(),"../.."))

batch_dir = os.path.join(
    base_dir,
    "data",
    "batch_simulated",
    analysis_name)


# In[5]:


get_ipython().run_cell_magic('time', '', '\nall_data_df = pd.DataFrame()\n\nfor i in num_batches:\n    print(\'Plotting PCA of 1 batch vs {} batches...\'.format(i))\n    \n    # Get batch 1 data\n    batch_1_file = os.path.join(\n        batch_dir,\n        "Batch_1.txt.xz")\n\n    batch_1 = pd.read_table(\n        batch_1_file,\n        header=0,\n        index_col=0,\n        sep=\'\\t\')\n\n    # Simulated data with all samples in a single batch\n    original_data_df =  batch_1.copy()\n    \n    # Add grouping column for plotting\n    original_data_df[\'group\'] = \'batch_1\'\n    \n    # Get data with additional batch effects added\n    batch_other_file = os.path.join(\n        batch_dir,\n        "Batch_"+str(i)+".txt.xz")\n\n    batch_other = pd.read_table(\n        batch_other_file,\n        header=0,\n        index_col=0,\n        sep=\'\\t\')\n    \n    # Simulated data with i batch effects\n    batch_data_df =  batch_other\n    \n    # Add grouping column for plotting\n    batch_data_df[\'group\'] = "batch_{}".format(i)\n    \n    # Concatenate datasets together\n    combined_data_df = pd.concat([original_data_df, batch_data_df])\n    \n    # PCA projection\n    pca = PCA(n_components=2)\n\n    # Encode expression data into 2D PCA space\n    combined_data_numeric_df = combined_data_df.drop([\'group\'], axis=1)\n    combined_data_PCAencoded = pca.fit_transform(combined_data_numeric_df)\n\n\n    combined_data_PCAencoded_df = pd.DataFrame(combined_data_PCAencoded,\n                                               index=combined_data_df.index,\n                                               columns=[\'PC1\', \'PC2\']\n                                              )\n    \n    # Add back in batch labels (i.e. labels = "batch_"<how many batch effects were added>)\n    combined_data_PCAencoded_df[\'group\'] = combined_data_df[\'group\']\n    \n    # Add column that designates which batch effect comparision (i.e. comparison of 1 batch vs 5 batches\n    # is represented by label = 5)\n    combined_data_PCAencoded_df[\'num_batches\'] = str(i)\n    \n    # Concatenate ALL comparisons\n    all_data_df = pd.concat([all_data_df, combined_data_PCAencoded_df])\n    \n    \n    # Plot individual comparisons\n    print(ggplot(combined_data_PCAencoded_df, aes(x=\'PC1\', y=\'PC2\')) \\\n          + geom_point(aes(color=\'group\'), alpha=0.4) \\\n          + xlab(\'PC1\') \\\n          + ylab(\'PC2\') \\\n          + ggtitle(\'Batch 1 and Batch {}\'.format(i))\n         )')


# In[6]:


# Plot all comparisons in one figure
ggplot(all_data_df, aes(x='PC1', y='PC2')) + geom_point(aes(color='group'), alpha=0.3) + facet_wrap('~num_batches') + xlab('PC1') + ylab('PC2') + ggtitle('PCA of batch 1 vs batch x')


# ## Permuted dataset (Negative control)
# 
# As a negative control we will permute the values within a sample, across genes in order to disrupt the gene expression structure.

# In[7]:


# Permute simulated data
shuffled_simulated_arr = []
num_samples = batch_1.shape[0]

for i in range(num_samples):
    row = list(batch_1.values[i])
    shuffled_simulated_row = random.sample(row, len(row))
    shuffled_simulated_arr.append(shuffled_simulated_row)

shuffled_simulated_data = pd.DataFrame(shuffled_simulated_arr, 
                                       index=batch_1.index,
                                       columns=batch_1.columns)
shuffled_simulated_data.head()


# In[8]:


# PCA

# label samples with label = perumuted
shuffled_simulated_data['group'] = "permuted"

# Concatenate original simulated data and shuffled simulated data
input_vs_permuted_df = pd.concat([original_data_df, shuffled_simulated_data])


input_vs_permuted = input_vs_permuted_df.drop(['group'], axis=1)
shuffled_data_PCAencoded = pca.fit_transform(input_vs_permuted)


shuffled_data_PCAencoded_df = pd.DataFrame(shuffled_data_PCAencoded,
                                           index=input_vs_permuted_df.index,
                                           columns=['PC1', 'PC2']
                                          )

# Add back in batch labels (i.e. labels = "batch_"<how many batch effects were added>)
shuffled_data_PCAencoded_df['group'] = input_vs_permuted_df['group']


# In[9]:


# Plot permuted data
print(ggplot(shuffled_data_PCAencoded_df, aes(x='PC1', y='PC2'))       + geom_point(aes(color='group'), alpha=0.4)       + xlab('PC1')       + ylab('PC2')       + ggtitle('Simulated vs Permuted')
     )

