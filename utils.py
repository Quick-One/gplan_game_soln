import matplotlib.pyplot as plt
import seaborn as sns
from solver import solve
import pathlib
from timeit import default_timer as timer
from fetch_data import processed_data
import numpy as np

def plot_solution(soln):
    sx, sy = soln.shape
    width = (60 * sy) / 100
    height = (60 * sx) / 100
    fig,ax = plt.subplots(1,1,figsize=(width, height))
    ntiles = soln.max() + 1 # adding 1 to accomodate for empty space
    annot = soln.astype(str)
    annot[annot == '0'] = ''
    ax = sns.heatmap(
        soln,
        annot=annot,
        cbar=False,
        cmap=sns.color_palette("muted", ntiles),
        fmt="",
        linewidths=2,
        linecolor='k',
        annot_kws={"color":"k"},
        alpha=1,
    )
    ax.tick_params(
        left=False, bottom=False,
        labelleft=False, labelright=False,
        labeltop=False,labelbottom=False
    )
    return fig, ax

def filter_interesting_solns(lvl, solns):
    _, _, _, rotate = processed_data(lvl)
    if not rotate:
        return solns
    # remove rotations
    def same(arr1, arr2):
        for _ in range(4):
            if np.array_equal(arr1, arr2):
                return True
            arr1 = np.rot90(arr1)
        return False
    
    interesting = []
    boolInteresting = [True] * len(solns)
    for i, soln1 in enumerate(solns):
        if boolInteresting[i]:
            interesting.append(soln1)
            for j in range(i+1, len(solns)):
                if not boolInteresting[i]:
                    continue
                soln2 = solns[j]
                if same(soln1, soln2):
                    boolInteresting[j] = False
    return interesting
    
def save_all_solns(levels):
    for lvl in range(1, levels+1):
        start = timer()
        solns = solve(lvl, one = False)
        end = timer()
        print(f"Level {lvl} solved in {end-start:.2f} seconds. {len(solns)} solutions found.")
        solns = filter_interesting_solns(lvl, solns)
        print(f"Level {lvl} has {len(solns)} interesting solutions.")
        for i, soln in enumerate(solns, start = 1):
            directory = pathlib.Path(f"./solutions/{lvl}")
            directory.mkdir(parents=True, exist_ok=True)
            fig, _ = plot_solution(soln)
            fig.savefig(directory / f"{i}.png", bbox_inches='tight', pad_inches=0)
            plt.close(fig)
