# Git Commit Contribution Heatmap

This script generates a heatmap visualizing your commit contributions over time in a specified Git repository. It filters commit dates based on the author's email and displays the number of commits per week and weekday.

![contribution_heatmap](https://github.com/user-attachments/assets/9bb3ba14-5599-4c07-b696-e11d36b71da7)

## Features

- Extracts commit dates from a Git repository using the author's email.
- Parses and organizes the commit data into a structured format.
- Generates a heatmap visualizing the commit contributions by week and weekday.

## Requirements

- Python 3.x
- `matplotlib`
- `seaborn`
- `pandas`

## Installation

To get started, clone the repository and install the required packages:

```bash
git clone https://github.com/mihai10001/contributions_graph
cd contributions_graph
pip install matplotlib seaborn pandas
```

## Usage

Run the script from the command line with the following syntax:

```bash
python generate_graph.py <path_to_your_repository> <your_email@example.com>
```

### Example

```bash
python generate_graph.py /path/to/your/repo your_email@example.com
```

This will generate a heatmap image named `contribution_heatmap.png` in the current directory.

## Output

The generated heatmap will show:

- **X-axis**: Weeks of the year with month labels
- **Y-axis**: Days of the week (Monday, Wednesday, Friday, Sunday)
- **Color intensity**: Represents the number of commits made on each day

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
