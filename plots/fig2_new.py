import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.lines import Line2D
from glob import glob
import scienceplots
import matplotlib.gridspec as gridspec
import scipy.stats as st
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.colors as colors
from functools import reduce
import torch
import math

def argsort(seq):
    # http://stackoverflow.com/questions/3071415/efficient-method-to-calculate-the-rank-vector-of-a-list-in-python
    return sorted(range(len(seq)), key=seq.__getitem__)

def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=100):
    new_cmap = colors.LinearSegmentedColormap.from_list(
        'trunc({n},{a:.2f},{b:.2f})'.format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)))
    return new_cmap

plt.style.use(['nature'])
fig = plt.figure(figsize=(7.08661, 5))

color_1 = '#69005f'
color_2 = '#ff506e'
color_3 = '#cbc9e2'
color_4 = 'C0'
color_5 = 'C1'

cmap1 = LinearSegmentedColormap.from_list("", ["white", color_1])
new_cmap1 = truncate_colormap(cmap1, 0.2, 1.0)
new_cmap0 = truncate_colormap(plt.get_cmap('Greys'), 0.2, 1.0)
gs = gridspec.GridSpec(3, 2, width_ratios=[0.6666, 0.3333])

centaur_70b = torch.load('../results/custom_metrics_full_log_likelihoods_marcelbinz-Llama-3.1-Centaur-70B-adapter.pth')
llama_70b = torch.load('../results/custom_metrics_full_log_likelihoods_unsloth-Meta-Llama-3.1-70B-bnb-4bit.pth')

df_exp = pd.read_csv('../experiments.csv', sep=';')
df_baseline = pd.read_csv('../results/all_data_baseline.csv')
df_baseline = df_baseline[df_baseline['unseen'] == 'participants'][['task', 'baseline']]

papers = []
results_centaur = []
results_centaur_se = []  
results_llama = []
for key in centaur_70b.keys():
    baseline = df_baseline[df_baseline['task'] == key]
    if len(baseline) > 0:
        papers.append(df_exp[df_exp['path'] == key + '/']['task_name'].item())
        print(key)
        print(centaur_70b[key].mean())
        print(baseline.baseline.item())
        print()
        centaur_relative = ((-centaur_70b[key] + baseline.baseline.item()) / baseline.baseline.item()) * 100
        llama_relative = ((-llama_70b[key] + baseline.baseline.item()) / baseline.baseline.item()) * 100
        results_centaur.append(centaur_relative.mean())
        results_centaur_se.append(centaur_relative.std() / math.sqrt(len(centaur_relative)))
        results_llama.append(llama_relative.mean())

ax1 = fig.add_subplot(gs[:, 0])

order = np.argsort(results_centaur)
papers = np.array(papers)[order]
results_centaur = np.array(results_centaur)[order] + 100
results_llama = np.array(results_llama)[order] + 100

custom_lines_r2 = [
    Line2D([0], [0], color=color_1, alpha=0.8, linewidth=5, markersize=5), 
    Line2D([0], [0], color=color_2, alpha=0.8, linewidth=5, markersize=5),
    Line2D([0], [0], color=color_3, linestyle='dashed', markersize=5)]


ax1.barh([len(results_centaur) + 1 ], [np.array(results_centaur).mean()], xerr=[np.array(results_centaur).std() / math.sqrt(len(results_centaur))],  height=0.75, color=color_1, alpha=0.8)
ax1.barh([len(results_llama) + 1], [np.array(results_llama).mean()], height=0.75, color=color_2, alpha=0.8)
ax1.barh(np.arange(len(results_centaur)), results_centaur, xerr=results_centaur_se, height=0.75, color=color_1, alpha=0.8)
ax1.barh(np.arange(len(results_llama)), results_llama, height=0.75, color=color_2, alpha=0.8)

ax1.set_yticks(np.arange(len(results_centaur)).tolist() + [len(results_centaur) + 1], papers.tolist() + ['Overall'])
ax1.set_xlabel('Relative log-likelihoods (%)')
ax1.set_xlim(50)
ax1.set_ylim(-0.5, len(results_centaur) + 2)
ax1.axvline(x=100, color='grey', linestyle='--', linewidth=1.0)
ax1.legend(custom_lines_r2, ['Centaur', 'Llama', 'Cognitive model'], frameon=False, ncols=1)

# subplot 2
centaur_rewards = np.concatenate([pd.read_csv('../openloop/results/baselines_openloop_centaur_twostep' + str(i) + '.csv')['reward'].values for i in range(1, 3)])
human_rewards = np.concatenate([pd.read_csv('../openloop/results/baselines_openloop_human_twostep' + str(i) + '.csv')['reward'].values for i in range(1, 3)])
rewards = np.concatenate((human_rewards, centaur_rewards))

centaur_mb = np.concatenate([pd.read_csv('../openloop/results/baselines_openloop_centaur_twostep' + str(i) + '.csv')['param'].values for i in range(1, 3)])
human_mb = np.concatenate([pd.read_csv('../openloop/results/baselines_openloop_human_twostep' + str(i) + '.csv')['param'].values for i in range(1, 3)])
model_basednesses = np.concatenate((human_mb, centaur_mb))

df = pd.DataFrame({'rewards': rewards, 'model_basednesses': model_basednesses, 'agent': ['Humans'] * 30 + ['Centaur 3.1'] * 30})
df['rewards'] = df['rewards'] * 2
humans = df.loc[df.agent == "Humans"]
centaur = df.loc[df.agent == "Centaur 3.1"]

ax2 = fig.add_subplot(gs[0, 1])
custom_lines = [Line2D([0], [0], color=color_1, alpha=0.8, marker="o", linestyle='None', markersize=5), Line2D([0], [0], color='grey', marker="o", linestyle='None', markersize=5)]
sns.kdeplot(x=humans.rewards, y=humans.model_basednesses, cmap=new_cmap0, shade=True, shade_lowest=False, ax=ax2, alpha=0.75)
sns.kdeplot(x=centaur.rewards, y=centaur.model_basednesses, cmap=new_cmap1, shade=True, shade_lowest=False, ax=ax2, alpha=0.75)
ax2.legend(custom_lines, ['Centaur', 'Humans'], columnspacing=0.7, frameon=False, ncols=2, bbox_to_anchor=(0.5, 1.2), loc='upper center')
ax2.set_xlabel('Reward')
ax2.set_xlim(0.1, 0.9)
ax2.set_ylabel('Model-basedness')
ax2.text(-0.13, 1.12, 'b', transform=ax2.transAxes, fontsize=8, fontweight='bold', va='top')
ax1.text(-2.52, 1.12, 'a', transform=ax2.transAxes, fontsize=8, fontweight='bold', va='top')

# subplot 3
centaur_rewards = np.concatenate([pd.read_csv('../openloop/results/baselines_openloop_centaur_horizon' + str(i) + '.csv')['reward'].values for i in range(1, 5)])
human_rewards = np.concatenate([pd.read_csv('../openloop/results/baselines_openloop_human_horizon' + str(i) + '.csv')['reward'].values for i in range(1, 5)])
rewards = np.concatenate((human_rewards, centaur_rewards))

centaur_ib = np.concatenate([pd.read_csv('../openloop/results/baselines_openloop_centaur_horizon' + str(i) + '.csv')['param'].values for i in range(1, 5)])
human_ib = np.concatenate([pd.read_csv('../openloop/results/baselines_openloop_human_horizon' + str(i) + '.csv')['param'].values for i in range(1, 5)])
information_bonus = np.concatenate((human_ib, centaur_ib))

df = pd.DataFrame({'rewards': rewards, 'information_bonus': information_bonus, 'agent': ['Humans'] * 28 + ['Centaur 3.1'] * 28})
humans = df.loc[df.agent == "Humans"]
centaur = df.loc[df.agent == "Centaur 3.1"]

ax3 = fig.add_subplot(gs[1, 1])
sns.kdeplot(x=humans.rewards, y=humans.information_bonus, cmap=new_cmap0, shade=True, shade_lowest=False, ax=ax3, alpha=0.75)
sns.kdeplot(x=centaur.rewards, y=centaur.information_bonus, cmap=new_cmap1, shade=True, shade_lowest=False, ax=ax3, alpha=0.75)
ax3.set_xlim(42, 62)
ax3.set_xlabel('Reward')
ax3.set_ylabel('Information bonus')
ax3.text(-0.13, 1.12, 'c', transform=ax3.transAxes, fontsize=8, fontweight='bold', va='top')

# subplot 4
df_centaur = pd.read_csv('../openloop/jansen2021dunningkruger/simulation.csv')
df_human = pd.read_csv("../openloop/jansen2021dunningkruger/exp1.csv")
df_human =  df_human.head(len(df_centaur))

centaur_predicted_scores = df_centaur[df_centaur['question'] == 'absAssess0'].choice.astype('float').values
human_predicted_scores =  df_human[df_human['question'] == 'absAssess0'].choice.astype('float').values
centaur_scores = df_centaur[df_centaur['question'] == 'score'].choice.astype('float').values
human_scores =  df_human[df_human['question'] == 'score'].choice.astype('float').values
scores = np.concatenate((human_scores, centaur_scores))
predicted_scores = np.concatenate((human_predicted_scores, centaur_predicted_scores))
df = pd.DataFrame({'predicted_scores': predicted_scores, 'scores': scores, 'agent': ['Humans'] * 1000 + ['Centaur 3.1'] * 1000})
humans = df.loc[df.agent == "Humans"]
centaur = df.loc[df.agent == "Centaur 3.1"]

ax4 = fig.add_subplot(gs[2, 1])
sns.kdeplot(x=humans.scores, y=humans.predicted_scores, cmap=new_cmap0, shade=True, shade_lowest=False, ax=ax4, alpha=0.75)
sns.kdeplot(x=centaur.scores, y=centaur.predicted_scores, cmap=new_cmap1, shade=True, shade_lowest=False, ax=ax4, alpha=0.75)
ax4.set_xlabel('True score')
ax4.set_ylabel('Estimated score')
ax4.text(-0.13, 1.12, 'd', transform=ax4.transAxes, fontsize=8, fontweight='bold', va='top')

plt.tight_layout()
sns.despine()
plt.savefig('figures/fig2_new.pdf', bbox_inches='tight')
plt.show()
