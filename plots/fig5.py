import pandas as pd
import jsonlines
from glob import glob
import numpy as np
import statsmodels.formula.api as sm
import pandas as pd
import jsonlines
from glob import glob
import numpy as np
import statsmodels.formula.api as sm
import matplotlib.pyplot as plt
import scienceplots
import matplotlib.gridspec as gridspec
import seaborn as sns

df = pd.read_csv('../experiments.csv', sep=';')
df['path'] = df['path'].str.replace('/','')
df = df.rename(columns={"path": "task"})
df_llms = pd.read_csv('../results/fig5_data.csv')

for index, row in df_llms.iterrows():
    df_llms.loc[index, 'num_actions'] = df[df['task'] == row['task']]['num_actions'].item()
    df_llms.loc[index, 'num_participants'] = df[df['task'] == row['task']]['num_participants'].item()
    df_llms.loc[index, 'num_choices'] = df[df['task'] == row['task']]['num_choices'].item()
    df_llms.loc[index, 'num_characters'] = df[df['task'] == row['task']]['num_characters'].item()
    df_llms.loc[index, 'task_type'] = df[df['task'] == row['task']]['task_type'].item()
    df_llms.loc[index, 'split'] = df[df['task'] == row['task']]['split'].item()

df_llms = df_llms[df_llms['split'] == 'train']
ll_centaur = -df_llms['/home/aih/marcel.binz/Centaur-3.1/1_finetuning/centaur2-final-llama/checkpoint-2000/']
ll_llama = -df_llms['unsloth/Meta-Llama-3.1-70B-bnb-4bit']
ll_random = -np.log(df_llms['num_actions'])
df_llms['r2_centaur'] = 1 - (ll_centaur/ll_random)
df_llms['r2_llama'] = 1 - (ll_llama/ll_random)
df_llms['r2_delta'] = df_llms['r2_centaur'] - df_llms['r2_llama']

print((df_llms['r2_delta'].values < 0).sum())
print(df_llms['r2_delta'].values.mean())
print(df_llms['r2_delta'].values.std())

result = sm.ols(formula="r2_delta ~ task_type + num_participants + num_choices + num_characters - 1", data=df_llms).fit()
print(result.summary())

result.params = result.params.set_axis(['Decision-making', 'Markov decision processes', 'Memory', 'Miscellaneous', 'Multi-armed bandits', 'Supervised learning', 'Participants', 'Choices', 'Characters'])
result.bse = result.bse.set_axis(['Decision-making', 'Markov decision processes', 'Memory', 'Miscellaneous', 'Multi-armed bandits', 'Supervised learning', 'Participants', 'Choices', 'Characters'])


plt.style.use(['nature'])
fig = plt.figure(figsize=(7.08661, 3))

gs = gridspec.GridSpec(1, 2, width_ratios=[0.5, 0.5])

ax = fig.add_subplot(gs[:, 0])
result.params[:6].plot(kind='bar',  yerr=result.bse[:6], ax=ax,legend=False, color='grey', alpha=0.8)
ax.text(-0.11, 1.11, 'a', transform=ax.transAxes, fontsize=8, fontweight='bold', va='top')  # Add label (b)
ax.set_ylim(0, 0.21)

ax = fig.add_subplot(gs[:, 1])
result.params[6:].plot(kind='bar', yerr=result.bse[6:], ax=ax,legend=False, color='grey', alpha=0.8)
ax.text(-0.11, 1.11, 'b', transform=ax.transAxes, fontsize=8, fontweight='bold', va='top')  # Add label (b)
ax.set_ylim(0, 3e-5)

plt.tight_layout()
sns.despine()
plt.savefig('figures/fig5.pdf', bbox_inches='tight')
plt.show()
