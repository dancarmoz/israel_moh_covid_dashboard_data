from datetime import datetime

from .csv_column_plot import CsvColumnPlot
from .modifiers import Multiply, Average, ChopFromEnd, Group
from .plot_viewer import PlotViewer


def expand_age_group(age_group):
    if age_group == '90+':
        return '90+'

    all_age_groups = (f'{r}-{r+9}' for r in range(0, 90, 10))
    all_age_groups = list(all_age_groups) + ['90+']

    index = int(age_group.split('+')[0]) // 10
    return all_age_groups[index:]


def add_verified_age_groups(viewer, start_date):

    age_groups = ('10-19', '20-29', '30-39', '40-49', '50-59', '60+')

    age_plots = []
    for age_group in age_groups:
        if '+' in age_group:
            # Group several age groups together
            grouped_plots = []
            for expanded_age_group in expand_age_group(age_group):
                grouped_plots.append(CsvColumnPlot(
                    start_date=start_date,
                    path='ages_dists.csv',
                    should_skip_first_line=True,
                    column=expanded_age_group))
            age_plots.append(Group(label=age_group, plots=grouped_plots))
        else:
            # Add individual age group
            age_plots.append(CsvColumnPlot(
                start_date=start_date,
                path='ages_dists.csv',
                should_skip_first_line=True,
                column=age_group))

    for age_plot in age_plots:
        viewer.add_plot(Average(7, ChopFromEnd(1, age_plot)))


def main():
    viewer = PlotViewer()

    start_date = datetime(2020, 12, 10)

    viewer.add_plot(Average(7, Multiply(20, ChopFromEnd(1, CsvColumnPlot(
            start_date=start_date,
            path='vaccinated.csv',
            column='Vaccinated population percentage')))))

    viewer.add_plot(Average(7, ChopFromEnd(1, CsvColumnPlot(
            start_date=start_date,
            path='hospitalized_and_infected.csv',
            column='Hospitalized'))))

    add_verified_age_groups(viewer, start_date)

    viewer.show()


if __name__ == '__main__':
    main()
