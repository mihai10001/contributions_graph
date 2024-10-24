import sys
import argparse
from datetime import datetime
import subprocess
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns

def get_commit_dates(repo_paths, your_email):
    all_commit_dates = []
    for repo_path in repo_paths:
        git_log_cmd = [
            "git", "-C", repo_path, "log", 
            "--pretty=format:%ad,%ae", "--date=iso", 
            "--author={}".format(your_email)
        ]
        try:
            git_log_output = subprocess.check_output(git_log_cmd).decode("utf-8")
            commit_dates = [line.split(',')[0] for line in git_log_output.splitlines()]
            all_commit_dates.extend(commit_dates)
        except subprocess.CalledProcessError as e:
            print(f"Error processing repository {repo_path}: {e}")
    return all_commit_dates

def parse_dates(commit_dates):
    parsed_dates = []
    for date in commit_dates:
        try:
            parsed_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S %z").date()
            parsed_dates.append(parsed_date)
        except ValueError:
            continue
    if not parsed_dates:
        raise ValueError("No valid commit dates found. Please check your repositories or email.")
    return parsed_dates

def create_commit_counts_df(parsed_dates):
    commit_series = pd.Series(parsed_dates)
    commit_counts = commit_series.value_counts().sort_index()
    all_dates = pd.date_range(start=commit_series.min(), end=commit_series.max())
    commit_counts = commit_counts.reindex(all_dates, fill_value=0)
    return pd.DataFrame({'date': commit_counts.index, 'count': commit_counts.values})

def enrich_commit_counts(commit_counts_df):
    commit_counts_df['week'] = commit_counts_df['date'].apply(lambda x: x.isocalendar()[1])
    commit_counts_df['year'] = commit_counts_df['date'].apply(lambda x: x.isocalendar()[0])
    commit_counts_df['month'] = commit_counts_df['date'].dt.month
    commit_counts_df['weekday'] = commit_counts_df['date'].apply(lambda x: x.weekday())
    return commit_counts_df.groupby(['year', 'week', 'weekday'])['count'].sum().reset_index()

def create_heatmap_data(commit_counts_grouped):
    return commit_counts_grouped.pivot(index='weekday', columns=['year', 'week'], values='count').fillna(0)

def get_month_labels(heatmap_data):
    month_labels = {}
    month_positions = []
    previous_month = None
    for idx, (year, week) in enumerate(heatmap_data.columns):
        start_date = datetime.fromisocalendar(year, week, 1)
        current_month = start_date.month
        if current_month != previous_month:
            month_positions.append(idx)
            month_labels[idx] = start_date.strftime('%b')
        previous_month = current_month
    return month_labels, month_positions

def create_transparent_cmap(cmap_name, alpha=1.0):
    base_cmap = plt.get_cmap(cmap_name)
    colors = base_cmap(np.linspace(0, 1, base_cmap.N))
    colors[:, -1] = np.linspace(0, alpha, base_cmap.N)
    return mcolors.ListedColormap(colors)

def plot_heatmap(heatmap_data, month_labels, month_positions, use_transparency):
    cmap = create_transparent_cmap('Greens', alpha=0.5) if use_transparency else 'Greens'
    linecolor = (0, 0, 0, 0.1) if use_transparency else (1, 1, 1, 1)
    tickscolor = 'white' if use_transparency else 'black'

    plt.figure(figsize=(len(month_labels) + 4, 3))
    sns.heatmap(
        heatmap_data,
        cmap=cmap,
        linewidths=0.1,
        linecolor=linecolor,
        cbar=False,
        square=True,
        yticklabels=['Mon', '', 'Wed', '', 'Fri', '', 'Sun'],
    )
    plt.gca().xaxis.set_ticks_position('top')
    plt.yticks(color=tickscolor)
    plt.xticks(month_positions, [month_labels[pos] for pos in month_positions], rotation=0, fontsize=12, color=tickscolor)
    plt.title('')
    plt.xlabel('')
    plt.ylabel('')
    plt.gca().tick_params(axis='both', which='both', length=0)
    plt.tight_layout()
    plt.savefig("contribution_heatmap.png", transparent=use_transparency)

def main():
    parser = argparse.ArgumentParser(description='Generate a contribution heatmap from git repositories.')
    parser.add_argument('repos', nargs='+', help='Paths to git repositories')
    parser.add_argument('email', help='Your email address used in the git commits')
    parser.add_argument('--transparent', action='store_true', help='Use transparency in heatmap (default: False)')
    args = parser.parse_args()
    repo_paths = args.repos
    your_email = args.email
    use_transparency = args.transparent

    commit_dates = get_commit_dates(repo_paths, your_email)
    parsed_dates = parse_dates(commit_dates)
    commit_counts_df = create_commit_counts_df(parsed_dates)
    commit_counts_grouped = enrich_commit_counts(commit_counts_df)
    heatmap_data = create_heatmap_data(commit_counts_grouped)
    month_labels, month_positions = get_month_labels(heatmap_data)
    plot_heatmap(heatmap_data, month_labels, month_positions, use_transparency)

if __name__ == "__main__":
    main()
