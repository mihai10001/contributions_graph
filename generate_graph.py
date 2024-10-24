import subprocess
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from datetime import datetime
import sys

def validate_input():
    if len(sys.argv) < 3:
        print("Usage: python script_name.py 'path/to/repo1' 'path/to/repo2' ... 'your_email@example.com'")
        sys.exit(1)

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

def plot_heatmap(heatmap_data, month_labels, month_positions):
    plt.figure(figsize=(len(month_labels) + 4, 3))
    sns.heatmap(
        heatmap_data,
        cmap="Greens",
        linewidths=0.1,
        linecolor='white',
        cbar=False,
        square=True,
        yticklabels=['Mon', '', 'Wed', '', 'Fri', '', 'Sun']
    )
    plt.gca().xaxis.set_ticks_position('top')
    plt.xticks(month_positions, [month_labels[pos] for pos in month_positions], rotation=0, fontsize=12)
    plt.title('')
    plt.xlabel('')
    plt.ylabel('')
    plt.gca().tick_params(axis='both', which='both', length=0)
    plt.tight_layout()
    plt.savefig("contribution_heatmap.png")

def main():
    validate_input()
    repo_paths = sys.argv[1:-1]  # Repositories
    your_email = sys.argv[-1]    # Email

    commit_dates = get_commit_dates(repo_paths, your_email)
    parsed_dates = parse_dates(commit_dates)
    commit_counts_df = create_commit_counts_df(parsed_dates)
    commit_counts_grouped = enrich_commit_counts(commit_counts_df)
    heatmap_data = create_heatmap_data(commit_counts_grouped)
    month_labels, month_positions = get_month_labels(heatmap_data)
    plot_heatmap(heatmap_data, month_labels, month_positions)

if __name__ == "__main__":
    main()
