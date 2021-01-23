import csv
from datetime import datetime, timedelta
import numpy
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


SPLIT = 7


def str_to_datetime(s):
    iso_datetime = s.replace('T', ' ').split('.')[0]
    return datetime.fromisoformat(iso_datetime)


def row_to_values(row):
    # values = row[1:SPLIT] + [sum(map(int, row[SPLIT:11]))]
    values = [sum(map(int, row[2:SPLIT]))] + [sum(map(int, row[SPLIT:11]))]
    return [int(v) for v in values]


def get_population_factors():
    population = [
        1735653,  # 0-9
        1442260,  # 10-19
        1237076,  # 20-29
        1158074,  # 30-39
        1033574,  # 40-49
        803246,   # 50-59
        704700,   # 60-69
        379700,   # 70-79
        243500,   # 80+
    ]

    # population = [
    #     0.48,  # 0-9
    #     0.21,  # 10-19
    #     0.25,  # 20-29
    #     0.35,  # 30-39
    #     0.38,  # 40-49
    #     0.49,   # 50-59
    #     0.70,   # 60-69
    #     0.9,   # 70-79
    #     1.2,   # 80+
    # ]

    return [1, 5.8]

    # population = population[0:SPLIT] + [sum(population[SPLIT:])]
    population = [sum(population[0:SPLIT])] + [sum(population[SPLIT:])]
    return [1 / p for p in population]


def read_ages(start_date, normalize, only_diff):
    reader = csv.reader(open('ages_dists.csv'))
    next(reader)  # Skip gender titles
    #titles = next(reader)[1:SPLIT] + [f'{SPLIT-1}0+']
    next(reader)  # Skip titles
    titles = [f'10-{SPLIT * 10 - 11}'] + [f'{SPLIT * 10 - 10}+']
    dates = []
    value_lists = [[] for _ in range(len(titles))]
    first = []

    if normalize:
        factors = get_population_factors()
    else:
        factors = [1] * len(titles)

    # Aggregate
    prev_values = None
    prev_date = None
    for row in reader:
        date = str_to_datetime(row[0])
        if date < start_date:
            continue

        if len(first) == 0:
            first = [v for v in row_to_values(row)]

        if prev_date and prev_date.strftime('%Y%m%d') == date.strftime('%Y%m%d'):
            # This is an update within the same-day - add to the previous value
            for i, value in enumerate(row_to_values(row)):
                if only_diff:
                    value_lists[i][-1] += (value - prev_values[i]) * factors[i]
                else:
                    value_lists[i][-1] += (value - first[i]) * factors[i]
        else:
            # This is a new day update
            dates.append(mdates.date2num(date))

            for i, value in enumerate(row_to_values(row)):
                if only_diff:
                    if prev_values is None:
                        value_lists[i].append(0)
                    else:
                        value_lists[i].append((value - prev_values[i]) * factors[i])
                else:
                    value_lists[i].append((value - first[i]) * factors[i])

        prev_values = [v for v in row_to_values(row)]
        prev_date = date

    return dates, titles, value_lists


def moving_average(x, w):
    return numpy.convolve(x, numpy.ones(w), 'valid') / w


def averager(value_lists, w):
    for value_list in value_lists:
        yield list(moving_average(value_list, w))


def vertical_span(plt, date, date_end, color):
    plt.axvspan(date, date_end, facecolor=color, alpha=0.5)
    plt.text(date, 150, '', rotation=90)


def vertical_line(plt, date, text, color):
    plt.axvline(x=date, color=color, alpha=0.5)
    plt.text(date, 350, text, rotation=90)


def draw_events(plt):
    vacc1_date = datetime(2021, 1, 1)
    vertical_line(plt, vacc1_date, 'Vaccine #1 (1 million)', 'g')
    vertical_line(plt, vacc1_date + timedelta(days=21), 'Vaccine #2', 'g')
    vertical_line(plt, vacc1_date + timedelta(days=28), 'Vaccine #2+week', 'g')

    partial_lockdown = '#f0cccc'
    full_lockdown = '#f08888'

    # Second lockdown
    vertical_span(plt, datetime(2020, 9, 18), datetime(2020, 9, 25), partial_lockdown)
    vertical_span(plt, datetime(2020, 9, 25), datetime(2020, 10, 13), full_lockdown)
    vertical_span(plt, datetime(2020, 10, 13), datetime(2020, 10, 17), partial_lockdown)

    # Third lockdown
    vertical_span(plt, datetime(2020, 12, 27), datetime(2021, 1, 8), partial_lockdown)
    vertical_span(plt, datetime(2021, 1, 8), datetime.now(), full_lockdown)


def main():

    # start_date = datetime(2020, 12, 15)
    start_date = datetime(2020, 9, 10)

    dates, titles, value_lists = read_ages(
        start_date=start_date,
        normalize=True,
        only_diff=True
    )

    avg_window = 7
    dates = dates[avg_window-1:]
    value_lists = list(averager(value_lists, avg_window))

    fig, ax = plt.subplots(figsize=(23, 10))

    for i, value_list in enumerate(value_lists):
        alpha = 0.8
        ax.scatter(dates, value_list, label=titles[i], alpha=alpha)
        line, = ax.plot(dates, value_list, 'o--', alpha=alpha)
        ax.text(
            dates[-1] + 1,
            value_list[-1] if i != 0 else value_list[-1] + 35,
            titles[i],
            fontsize=11,
            color=line.get_color())

    # ax.stackplot(dates, value_lists, labels=titles)

    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(dates) // 30)))

    ax.set_ylabel(f'{avg_window}-day rolling daily cases')

    ax.legend(loc='upper left')
    ax.grid(True)

    fig.autofmt_xdate()

    draw_events(plt)

    plt.show()


if __name__ == '__main__':
    with plt.xkcd():
        main()
