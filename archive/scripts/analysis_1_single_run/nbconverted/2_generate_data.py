
# coding: utf-8

# # Generate data and calculate similarity
# 
# The goal of this notebook is to determine how much of the structure in the original dataset (single experiment) is retained after adding some number of experiments.
# 
# For this simulation experiment we wanted to capture the individual experiment structure.
# In particular, we simulated data by (1) preserving the relationship between samples within an experiment but (2) shifting the samples in space.
# 
# Criteria (1) will account for the type of experiment, such as treatment vs non-treatment.  Criteria (2) will reflect a different type of perturbation, like a different antibiotic.  
# 
# The approach is to,
# 1. Randomly sample an experiment from the Pseudomonas compendium
# 2. Embed samples from the experiment into the trained latent space
# 3. Randomly shift the samples to a new location in the latent space. This new location will be selected based on the distribution of samples in the latent space 

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

from plotnine import (ggplot, 
                      labs,  
                      geom_line, 
                      aes, 
                      ggsave, 
                      theme_bw,
                      theme,
                      element_text,
                      element_rect,
                      element_line)

sys.path.append("../")
from functions import generate_data
from functions import similarity_metric

from numpy.random import seed
randomState = 123
seed(randomState)


# In[2]:


# User parameters
NN_architecture = 'NN_2500_30'
analysis_name = 'analysis_1'
num_simulated_experiments = 600
lst_num_partitions = [1,2,3,5,10,20,30,50,70,100,200,300,400,500,600]
use_pca = True
num_PCs = 10


# In[3]:


# Input files

# base dir on repo
base_dir = os.path.abspath(os.path.join(os.getcwd(),"../..")) 

# base dir on local machine for data storage
# os.makedirs doesn't recognize `~`
local_dir = local_dir = os.path.abspath(os.path.join(os.getcwd(), "../../../..")) 

NN_dir = base_dir + "/models/" + NN_architecture

normalized_data_file = os.path.join(
    base_dir,
    "data",
    "input",
    "train_set_normalized.pcl")


# In[24]:


# Output file
svcca_file = os.path.join(
    local_dir,
    "Data",
    "Batch_effects",
    "output",
    "analysis_1_svcca.png")

svcca_blk_file = os.path.join(
    local_dir,
    "Data",
    "Batch_effects",
    "output",
    "analysis_1_svcca_blk.png")

similarity_uncorrected_file = os.path.join(
    local_dir,
    "Data",
    "Batch_effects",
    "output",
    "analysis_1_similarity_uncorrected.pickle")

permuted_score_file = os.path.join(
    local_dir,
    "Data",
    "Batch_effects",
    "output",
    "analysis_1_permuted.txt")


# ### Load file with experiment ids

# In[5]:


experiment_ids_file = os.path.join(
    base_dir,
    "data",
    "metadata",
    "experiment_ids.txt")


# ### Generate simulated data

# In[6]:


# Generate simulated data
generate_data.simulate_compendium(experiment_ids_file, 
                                  num_simulated_experiments,
                                  normalized_data_file,
                                  NN_architecture,
                                  analysis_name
                                 )


# In[7]:


# Simulated data file 
simulated_data_file = os.path.join(
    local_dir,
    "Data",
    "Batch_effects",
    "simulated",
    analysis_name,
    "simulated_data.txt.xz")


# In[8]:


# Read in data
simulated_data = pd.read_table(
    simulated_data_file,
    header=0,
    index_col=0,
    sep='\t')

simulated_data.head()


# In[9]:


ids = set([i.split("_")[0] for i in simulated_data['experiment_id']])
len(ids)     
#simulated_data['experiment_id'].sort_values()


# In[10]:


normalized_data = pd.read_table(
        normalized_data_file,
        header=0,
        sep='\t',
        index_col=0).T

normalized_data.head()


# ### Generate permuted version of simulated data (negative control)

# In[11]:


# Permute simulated data to be used as a negative control
generate_data.permute_data(simulated_data_file,
                          local_dir,
                          analysis_name)


# In[12]:


# Permuted simulated data file 
permuted_simulated_data_file = os.path.join(
    local_dir,
    "Data",
    "Batch_effects",
    "simulated",
    analysis_name,
    "permuted_simulated_data.txt.xz")


# In[13]:


# Read in data
permuted_data = pd.read_table(
    permuted_simulated_data_file,
    header=0,
    index_col=0,
    sep='\t')

permuted_data.head()


# ### Partition experiments in simulated data and add technical variation
# 
# For this simulation experiment we want to capture the experiment-level information.  In []() we divided our samples into experiments, we divide the experiments (by experiment id) into partitions where each partition is capturing a source of technical variation (i.e. these 3 experiments came from lab A and these other 3 experiments came from lab B and so lab A and B are our partitions).

# In[14]:


# Add technical variation to partitions
generate_data.add_experiments_grped(simulated_data_file,
                                    lst_num_partitions,
                                    local_dir,
                                    analysis_name)


# ### Calculate similarity

# In[15]:


# Calculate similarity
similarity_scores, permuted_score = similarity_metric.sim_svcca(simulated_data_file,
                                                           permuted_simulated_data_file,
                                                           'Partition',
                                                           lst_num_partitions,
                                                           use_pca,
                                                           num_PCs,
                                                           local_dir,
                                                           analysis_name)


# In[16]:


# Convert similarity scores to pandas dataframe
similarity_score_df = pd.DataFrame(data={'score': similarity_scores},
                                     index=lst_num_partitions,
                                   columns=['score'])
similarity_score_df.index.name = 'number of partitions'
similarity_score_df


# In[17]:


print("Similarity between input vs permuted data is {}".format(permuted_score))


# In[18]:


# Plot
threshold = pd.DataFrame(
    pd.np.tile(
        permuted_score,
        (len(lst_num_partitions), 1)),
    index=lst_num_partitions,
    columns=['score'])

g = ggplot(similarity_score_df, aes(x=lst_num_partitions, y='score'))     + geom_line()     + geom_line(aes(x=lst_num_partitions, y='score'), threshold, linetype='dashed')     + labs(x = "Number of Partitions", 
           y = "Similarity score (SVCCA)", 
           title = "Similarity across varying numbers of partitions") \
    + theme_bw() \
    + theme(plot_title=element_text(weight='bold'))

print(g)
ggsave(plot=g, filename=svcca_file, dpi=300)


# In[22]:


# Plot - black
threshold = pd.DataFrame(
    pd.np.tile(
        permuted_score,
        (len(lst_num_partitions), 1)),
    index=lst_num_partitions,
    columns=['score'])

g = ggplot(similarity_score_df, aes(x=lst_num_partitions, y='score'))     + geom_line(color="white")     + geom_line(threshold, aes(x=lst_num_partitions, y='score'), color="white", linetype='dashed')     + labs(x = "Number of Partitions", 
           y = "Similarity score (SVCCA)", 
           title = "Similarity across varying numbers of partitions") \
    + theme(plot_title=element_text(weight='bold', colour="white"),
            plot_background=element_rect(fill="black"),
            panel_background=element_rect(fill="black"),
            axis_title_x=element_text(colour="white"),
            axis_title_y=element_text(colour="white"),
            axis_line=element_line(color="white"),
            axis_text=element_text(color="white")
           )


print(g)
ggsave(plot=g, filename=svcca_blk_file, dpi=300)


# In[25]:


# Pickle similarity scores to overlay uncorrected and corrected svcca curves
similarity_score_df.to_pickle(similarity_uncorrected_file)
np.save(permuted_score_file, permuted_score)

