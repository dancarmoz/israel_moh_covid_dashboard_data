from datetime import datetime

from .csv_column_plot import CsvColumnPlot
from .modifiers import Multiply, Average, ChopFromEnd, OnlyFromDate, Group, DeriveToDays
from .plot_viewer import PlotViewer
from .plot_utils import normalize_plots_to_date


def expand_age_group(age_group):
    if age_group == '90+':
        return '90+'

    all_age_groups = (f'{r}-{r+9}' for r in range(0, 90, 10))
    all_age_groups = list(all_age_groups) + ['90+']

    index = int(age_group.split('+')[0]) // 10
    return all_age_groups[index:]


def get_age_group_plots(age_groups):
    age_plots = []
    for age_group in age_groups:
        if '+' in age_group:
            # Group several age groups together
            grouped_plots = []
            for expanded_age_group in expand_age_group(age_group):
                grouped_plots.append(CsvColumnPlot(
                    path='ages_dists.csv',
                    should_skip_first_line=True,
                    column=expanded_age_group))
            age_plots.append(DeriveToDays(Group(label=age_group, plots=grouped_plots)))
        else:
            # Add individual age group
            age_plots.append(DeriveToDays(CsvColumnPlot(
                path='ages_dists.csv',
                should_skip_first_line=True,
                column=age_group)))
    return age_plots


def main():
    viewer = PlotViewer()

    # Add Vaccinated
    viewer.add_plot(Multiply(10, CsvColumnPlot(
            path='vaccinated.csv',
            column='Second dose population precentage')))

    # Add Hospitalized
    viewer.add_plot(Multiply(0.5, CsvColumnPlot(
            path='hospitalized_and_infected.csv',
            column='Hospitalized')))

    # Add age groups
    age_plots = get_age_group_plots(('10-19', '20-29', '30-39', '40-49', '50-59', '60+'))
    age_plots = normalize_plots_to_date(datetime(2020, 10, 1), age_plots)
    viewer.add_plots(age_plots)

    # Apply global modifiers
    viewer.plots = [
        Average(7, OnlyFromDate(datetime(2020, 9, 1), plot)) for plot in viewer.plots
    ]

    viewer.show()


if __name__ == '__main__':
    main()
