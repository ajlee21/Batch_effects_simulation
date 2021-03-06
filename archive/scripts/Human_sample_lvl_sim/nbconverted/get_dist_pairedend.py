
# coding: utf-8

# # Get number of experiments using pairedend reads
# This notebook parses the metadata file associated with the recount2 data to determine the number of experiments using pairedend vs single-end reads.

# In[ ]:


import os
import sys
import pandas as pd

from numpy.random import seed
randomState = 123
seed(randomState)

sys.path.append("../../")
from functions import utils

import warnings
warnings.filterwarnings(action='ignore')


# In[ ]:


# Read in config variables
config_file = os.path.abspath(os.path.join(os.getcwd(),"../..", "config.tsv"))
params = utils.read_config(config_file)


# In[2]:


# Load parameters
dataset_name = params["dataset_name"]


# In[3]:


# Load arguments
base_dir = os.path.abspath(os.path.join(os.getcwd(),"../.."))

experiment_ids_file = os.path.join(
    base_dir,
    dataset_name,
    "data",
    "metadata",
    "recount2_experiment_ids.txt")

metadata_file = os.path.join(
    base_dir,
    dataset_name,
    "data",
    "metadata",
    "recount2_metadata.tsv")


# In[4]:


# Read data
experiment_ids = pd.read_table(
    experiment_ids_file,
    header=0,
    sep='\t',
    index_col=0)

metadata = pd.read_table(
    metadata_file,
    header=0,
    sep='\t',
    index_col=0)

experiment_ids.head()


# In[5]:


metadata.head()


# In[9]:


metadata.loc[list(experiment_ids['experiment_id'])]
#for experiment_id in list(experiment_ids['experiment_id']):
#    print(metadata[metadata['run'] == experiment_id])


# In[14]:


metadata.loc[list(experiment_ids['experiment_id'])]['paired_end'].value_counts()


# In[ ]:


metadata.head()

