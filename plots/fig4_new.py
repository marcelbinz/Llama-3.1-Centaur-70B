import matplotlib.pyplot as plt
import torch
import seaborn as sns
import scienceplots
import matplotlib.gridspec as gridspec
import matplotlib.colors as colors
import glob
from natsort import natsorted
import pandas as pd
import numpy as np
from sklearn.manifold import MDS
import math

gs = gridspec.GridSpec(1, 4, width_ratios=[0.25, 0.25, 0.25, 0.25])
plt.style.use(['nature'])
fig = plt.figure(figsize=(7.08661, 7.08661/4))

# plot MDS
metrics_df = pd.read_csv('../results/CogBench/behaviour.csv')
metrics_df = metrics_df.loc[:, ~metrics_df.columns.str.contains('^Unnamed')]
colors = ['black' for _ in metrics_df.Agent]
colors = ['grey' if engine in ['Human'] else color for engine, color in zip(metrics_df.Agent, colors)]
colors = ['#69005f' if engine == 'Centaur' else color for engine, color in zip(metrics_df.Agent, colors)]
colors = ['#ff506e' if engine == 'Llama' else color for engine, color in zip(metrics_df.Agent, colors)]

reducer = MDS(n_components=2, random_state=1)
metrics_scores = metrics_df.iloc[:, 1:metrics_df.shape[1]//2].values
agent_names = metrics_df.iloc[:, 0].values
embedding = reducer.fit_transform(metrics_scores)

ax = fig.add_subplot(gs[:, 0])
ax.scatter(embedding[:, 0], embedding[:, 1], c=colors, s=25, alpha=0.8)
ax.set_xlabel('Embedding dimension 1')
ax.set_ylabel('Embedding dimension 2')
ax.set_xlim(-4, 6)
ax.set_ylim(-4, 6)

for i in range(embedding.shape[0]):
    if agent_names[i] == 'GPT-3.5':
        ax.annotate(agent_names[i], (-0.6 + embedding[i, 0], embedding[i, 1]+0.5), size=5)
    else:
        ax.annotate(agent_names[i], (0.45 + embedding[i, 0], embedding[i, 1]-0.25),  size=5)

red_point = embedding[[engine == 'Llama' for engine in metrics_df.Agent]]
green_point = embedding[[engine == 'Centaur' for engine in metrics_df.Agent]]

ax.text(-0.22, 1.09, 'a', transform=ax.transAxes, fontsize=8, fontweight='bold', va='top')  # Add label (b)

if red_point.size > 0 and green_point.size > 0:
    plt.arrow(
        red_point[0, 0], red_point[0, 1],
        green_point[0, 0] - red_point[0, 0], green_point[0, 1] - red_point[0, 1],
        head_width=0.4, head_length=0.4, overhang=0, fc='k', length_includes_head=True
    )

#plot feher da silva
df_centaur_tst = pd.read_csv('../results/feher2023rethinking/schaefer_tst_centaur_alignment.csv')
df_llama_tst = pd.read_csv('../results/feher2023rethinking/schaefer_tst_llama_alignment.csv')
df_random_tst = pd.read_csv('../results/feher2023rethinking/schaefer_tst_random_alignment.csv')
twostep_centaur = df_centaur_tst.values.mean(1)
twostep_llama = df_llama_tst.values.mean(1)
twostep_random = df_random_tst.values.mean(1)
twostep_centaur_se = df_centaur_tst.values.std(1) / math.sqrt(df_centaur_tst.values.shape[1])
twostep_llama_se = df_llama_tst.values.std(1) / math.sqrt(df_centaur_tst.values.shape[1])
twostep_random_se = df_random_tst.values.std(1) / math.sqrt(df_random_tst.values.shape[1])

baseline_model = 0.20065425519568694
print(twostep_llama)
print(twostep_centaur)

ax = fig.add_subplot(gs[:, 1])
ax.errorbar([0, 10, 20, 30, 40], twostep_centaur, yerr=twostep_centaur_se, color='#69005f', alpha=0.8, linewidth=1)
ax.errorbar([0, 10, 20, 30, 40], twostep_llama, yerr=twostep_llama_se, color='#ff506e', alpha=0.8, linewidth=1)
ax.errorbar([0, 10, 20, 30, 40], twostep_random, yerr=twostep_random_se, color='grey', alpha=0.8, linewidth=1)
#ax.legend(['Centaur', 'Llama', 'Random initialization'], frameon=False, ncols=3, borderaxespad=0, handlelength=1, columnspacing=0.7, handletextpad=0.5, bbox_to_anchor=(0.51, 1.125), loc='upper center')
ax.axhline(y=baseline_model, color='grey', linestyle='--', linewidth=1.0)
ax.text(41, baseline_model - 0.0585, 'Cognitive model', fontsize=6, color='grey', horizontalalignment='right')
ax.text(-0.2, 1.09, 'b', transform=ax.transAxes, fontsize=8, fontweight='bold', va='top')  # Add label (b)
ax.set_ylabel('Pearson correlation')
ax.set_xlabel('Layer')
ax.set_xlim(1, 41)
ax.set_ylim(-0.05, 0.65)


# plot tuckute
reading_llama = torch.load('../results/tuckute2024driving/llama.pth')
reading_centaur = torch.load('../results/tuckute2024driving/centaur2000.pth')
reading_random = torch.load('../results/tuckute2024driving/random.pth')

ax = fig.add_subplot(gs[:, 2])
ax.plot(torch.arange(1, reading_centaur.shape[0] + 1), reading_centaur, color='#69005f', alpha=0.8, linewidth=1)
ax.plot(torch.arange(1, reading_llama.shape[0] + 1), reading_llama, color='#ff506e', alpha=0.8, linewidth=1)
ax.plot(torch.arange(1, reading_random.shape[0] + 1), reading_random, color='grey', alpha=0.8, linewidth=1)
ax.axhline(y=0.38, color='grey', linestyle='--', linewidth=1.0)
ax.axhline(y=0.56, color='black', linestyle='--', linewidth=1.0)
ax.text(41, 0.321, 'Tuckute et al. (2024)', fontsize=6, color='grey', horizontalalignment='right')
ax.text(41, 0.57, 'Noise ceiling', fontsize=6, color='black', horizontalalignment='right')
ax.text(-0.2, 1.09, 'c', transform=ax.transAxes, fontsize=8, fontweight='bold', va='top')  # Add label (b)
ax.set_ylabel('Pearson correlation')
ax.set_xlabel('Layer',)
ax.set_xlim(1, 41)
ax.set_ylim(-0.05, 0.63)
#ax.legend(['Centaur', 'Llama'], frameon=False, ncols=2, borderaxespad=0, handlelength=1, columnspacing=0.7, handletextpad=0.5, bbox_to_anchor=(0.51, 1.125), loc='upper center')

ax = fig.add_subplot(gs[:, 3])
coef, coef_se = np.load('../results/rt_regression_coef.npy')
ax.text(-0.2, 1.09, 'd', transform=ax.transAxes, fontsize=8, fontweight='bold', va='top')  # Add label (b)
ax.bar(np.arange(5), coef, yerr=coef_se, color='#69005f', alpha=0.8)
ax.set_ylabel('Regression coefficient')
ax.set_xticks(np.arange(5), ['SS', 'SC', 'RS', 'RC', 'Trial'],)

sns.despine()
plt.tight_layout()
plt.savefig('figures/fig4_new.pdf', bbox_inches='tight')

plt.show()
