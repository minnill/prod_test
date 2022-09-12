# -*- coding: utf-8 -*-
"""Untitled2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1iXfy_JpUGxdxDo1PfnLOo1_tgUV68yIm
"""

# clean the data: Ensure the data aligns with the metric definitions determined during the experiment design
# roughly equal num of users,

import pandas as pd
import math
import statsmodels.stats.api as sms
import scipy.stats as st

raw_data = pd.read_csv("ab_data.csv")
df = raw_data.copy()
print("Number of rows: ", df.shape[0], " Number of columns: ", df.shape[1])
df.head()

df['group'].value_counts()

#some of the control group saw the new_page and some tretment group saw the old_page - delete these instances
mask1 = (df["group"] == "control") & (df["landing_page"] == "new_page")
index_to_drop1 = df[mask1].index
df = df.drop(index_to_drop1)

mask2 = (df["group"] == "treatment") & (df["landing_page"] == "old_page")
index_to_drop2 = df[mask2].index
df = df.drop(index_to_drop2)

print(df.shape)
df["group"].value_counts()

#Check how many duplicated users exist
print(df["user_id"].count())
print(df["user_id"].nunique())

#drop duplicated users
df.drop_duplicates(subset ='user_id',keep ='first',inplace = True)

# pooled probability

mask = (df["group"] == "control")
conversions_control = df["converted"][mask].sum()
total_users_control = df["converted"][mask].count()

mask = (df["group"] == "treatment")
conversions_treatment = df["converted"][mask].sum()
total_users_treatment = df["converted"][mask].count()

print("Split of control users who saw old page vs treatment users who saw new page: ", 
          round(total_users_control / df["converted"].count() * 100, 2), "% ",
          round((total_users_treatment / df["converted"].count()) * 100, 2), "%")

#count number of users who converted in each group
print("Number of control users who converted on old page: ", conversions_control)
print("Percentage of control users who converted: ", round((conversions_control / total_users_control) * 100, 2), "%")

mask = (df["group"] == "treatment")
print("Number of treatment users who converted on new page: ", conversions_treatment)
print("Percentage of treatment users who converted: ", round((conversions_treatment/ total_users_treatment) * 100, 2), "%")

# check what sample size is required

# baseline rate: an estimate of the metric being analyzed before making any changes --> convertion rate of control group
# practical significant level: The minimum change to the baseline rate that is useful to the business,--> conversion rate of tratement group - conversion rate of control group
# confidence level: siginificance level --> null is rejected when it shouldn't be
# sensitivity: null is not rejected when it should be. 




baseline_rate = conversions_control / total_users_control
practical_significance = 0.01
confidence_level = 0.05
sensitivity = 0.8

effect_size = sms.proportion_effectsize(baseline_rate, baseline_rate + practical_significance)
sample_size = sms.NormalIndPower().solve_power(effect_size = effect_size, power = sensitivity, alpha = confidence_level, ratio=1)

print("Required sample size: ", round(sample_size), " per group")

prob_pooled = (conversions_control + conversions_treatment) / (total_users_control + total_users_treatment)

prob_pooled

se_pooled = math.sqrt(prob_pooled * (1-prob_pooled) * (1/total_users_control + 1 / total_users_treatment))
z_score = st.norm.ppf(1-confidence_level/2)
margin_of_error = se_pooled * z_score

#Calculate dhat, the estimated difference between probability of conversions in the experiment and control groups
d_hat = (conversions_treatment / total_users_treatment) - (conversions_control / total_users_control)
d_hat

#Test if we can reject the null hypothesis
lower_bound = d_hat - margin_of_error
upper_bound = d_hat + margin_of_error

if practical_significance < lower_bound:
    print("Reject null hypothesis")
else: 
    print("Do not reject the null hypothesis")
    
print("The lower bound of the confidence interval is ", round(lower_bound * 100, 2), "%")
print("The upper bound of the confidence interval is ", round(upper_bound * 100, 2), "%")

