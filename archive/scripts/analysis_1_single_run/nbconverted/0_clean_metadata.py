
# coding: utf-8

# # Process metadata
# 
# Not all experiment ids in the metadata file have corresponding gene expression data.  This notebook checks each experiment id and returns a clean list of experiment ids that have gene expression data.  This file will be used in ```2_generate_data.ipynb```

# In[1]:


get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')

import os
import sys
import glob
import pandas as pd
import numpy as np
import random

import warnings
warnings.filterwarnings(action='ignore')

sys.path.append("../")
from functions import generate_data
from functions import similarity_metric

from numpy.random import seed
randomState = 123
seed(randomState)


# In[2]:


# Input files

# base dir on repo
base_dir = os.path.abspath(os.path.join(os.getcwd(),"../..")) 

# base dir on local machine for data storage
# os.makedirs doesn't recognize `~`
local_dir = local_dir = os.path.abspath(os.path.join(os.getcwd(), "../../../..")) 

mapping_file = os.path.join(
    base_dir,
    "data",
    "metadata",
    "sample_annotations.tsv")

normalized_data_file = os.path.join(
    base_dir,
    "data",
    "input",
    "train_set_normalized.pcl")


# In[3]:


# Output file
experiment_id_file = os.path.join(
    base_dir, 
    "data",
    "metadata", 
    "experiment_ids.txt")


# ### Get experiment ids

# In[4]:


# Read in metadata
metadata = pd.read_table(
    mapping_file, 
    header=0, 
    sep='\t', 
    index_col=0)

metadata.head()


# In[5]:


map_experiment_sample = metadata[['sample_name', 'ml_data_source']]
map_experiment_sample.head()


# In[6]:


experiment_ids = np.unique(np.array(map_experiment_sample.index))
print("There are {} experiments in the compendium".format(len(experiment_ids)))


# ### Get sample ids from gene expression data

# In[7]:


normalized_data = pd.read_table(
    normalized_data_file,
    header=0,
    sep='\t',
    index_col=0).T

normalized_data.head()


# In[8]:


sample_ids_with_gene_expression = list(normalized_data.index)


# ### Get samples belonging to selected experiment

# In[9]:


experiment_ids_with_gene_expression = []

for experiment_id in experiment_ids:
    selected_metadata = metadata.loc[experiment_id]
    
    #print("There are {} samples in experiment {}".format(selected_metadata.shape[0], experiment_id))
    
    sample_ids = list(selected_metadata['ml_data_source'])
    
    if any(x in sample_ids_with_gene_expression for x in sample_ids):
        experiment_ids_with_gene_expression.append(experiment_id)
        
print('There are {} experiments with gene expression data'.format(len(experiment_ids_with_gene_expression)))


# In[10]:


experiment_ids_with_gene_expression_df = pd.DataFrame(experiment_ids_with_gene_expression, columns=['experiment_id'])
experiment_ids_with_gene_expression_df.head()


# In[11]:


# Save simulated data
experiment_ids_with_gene_expression_df.to_csv(experiment_id_file, sep='\t')

