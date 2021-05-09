import numpy as np
import calendar
import datetime
import matplotlib.pyplot as plt
from typing import List, Any, Optional, Union, Tuple
from matplotlib.pyplot import Axes
from matplotlib.colors import LinearSegmentedColormap, ListedColormap
from july.helpers import (
    date_grid,
    cal_heatmap,
    get_month_outline,
    get_calendar_title,
)
from july.utils import preprocess_inputs, preprocess_month
from july.rcmod import update_rcparams


def heatmap(
    dates: List[Union[str, datetime.date, datetime.datetime]],
    data: List[float],
    horizontal: bool = True,
    cmap: Union[str, LinearSegmentedColormap, ListedColormap] = "july",
    value_label: bool = False,
    date_label: bool = False,
    weekday_label: bool = True,
    month_label: bool = True,
    year_label: bool = True,
    month_grid: bool = False,
    colorbar: bool = False,
    frame_on: bool = False,
    value_format: str = "int",
    title: Optional[str] = None,
    cmin: Optional[int] = None,
    cmax: Optional[int] = None,
    ax: Optional[Axes] = None,
    **kwargs
) -> Axes:
    update_rcparams(**kwargs)
    dates_clean, data_clean = preprocess_inputs(dates, data)
    cal = date_grid(dates_clean, data_clean, horizontal)
    ax = cal_heatmap(
        cal=cal,
        dates=dates_clean,
        horizontal=horizontal,
        cmap=cmap,
        value_label=value_label,
        date_label=date_label,
        weekday_label=weekday_label,
        month_label=month_label,
        year_label=year_label,
        month_grid=month_grid,
        colorbar=colorbar,
        frame_on=frame_on,
        value_format=value_format,
        title=title,
        cmin=cmin,
        cmax=cmax,
        ax=ax,
    )

    return ax


def month_plot(
    dates: List[Union[str, datetime.date, datetime.datetime]],
    data: List[Any],
    horizontal: bool = False,
    cmap: Union[str, LinearSegmentedColormap, ListedColormap] = "july",
    value_label: bool = False,
    date_label: bool = False,
    weeknum_label: bool = True,
    month_label: bool = True,
    cal_mode: bool = False,
    value_format: str = "int",
    colorbar: bool = False,
    title: Optional[str] = None,
    month: Optional[int] = None,
    cmin: Optional[int] = None,
    cmax: Optional[int] = None,
    ax: Optional[Axes] = None,
    **kwargs
) -> Axes:
    update_rcparams(**kwargs)
    dates_clean, data_clean = preprocess_inputs(dates, data)
    month = month or dates_clean[0].month
    dates_mon, data_mon = preprocess_month(dates_clean, data_clean, month=month)
    month_grid = date_grid(dates_mon, data_mon, horizontal=horizontal)
    weeknum_grid = date_grid(
        dates_mon, [d.isocalendar()[1] for d in dates_mon], horizontal=horizontal
    )
    weeknum_labels: List[Any] = [
        int(x) for x in np.unique(weeknum_grid) if np.isfinite(x)
    ]

    if cal_mode:
        # Pad all grids to have six rows so weeks align when plotted side by side.
        while len(month_grid) < 6:
            month_grid = np.vstack([month_grid, 7 * [np.nan]])
            weeknum_labels.append("")

    if not ax:
        _, ax = plt.subplots(figsize=(5, 4))

    ax = cal_heatmap(
        cal=month_grid,
        dates=dates_mon,
        horizontal=horizontal,
        cmap=cmap,
        value_label=value_label,
        value_format=value_format,
        date_label=date_label,
        year_label=False,
        month_label=False,
        frame_on=False,
        colorbar=colorbar,
        cmin=cmin,
        cmax=cmax,
        ax=ax,
    )

    ax.tick_params(axis="y", pad=8)

    if weeknum_label:
        if horizontal:
            ax.set_xticks([i + 0.5 for i in range(month_grid.shape[1])])
            ax.set_xticklabels(weeknum_labels)
        else:
            ax.set_yticks([i + 0.5 for i in range(month_grid.shape[0])])
            ax.set_yticklabels(weeknum_labels)

    outline_coords = get_month_outline(dates_mon, month_grid, horizontal, month)
    ax.plot(outline_coords[:, 0], outline_coords[:, 1], color="black", linewidth=1)
    ax.set_xlim(ax.get_xlim()[0] - 0.1, ax.get_xlim()[1] + 0.1)
    ax.set_ylim(ax.get_ylim()[0] + 0.1, ax.get_ylim()[1] - 0.1)
    if month_label:
        ax.set_title(calendar.month_name[month])
    if title:
        plt.suptitle(title, y=1.07, size="x-large")

    return ax


def calendar_plot(
    dates: List[Union[str, datetime.date, datetime.datetime]],
    data: List[Any],
    cmap: Union[str, LinearSegmentedColormap, ListedColormap] = "july",
    value_label: bool = False,
    date_label: bool = False,
    value_format: str = "int",
    title: bool = True,
    ncols: int = 4,
    figsize: Optional[Tuple[float, float]] = None,
    **kwargs
) -> Axes:
    update_rcparams(**kwargs)
    dates_clean, data_clean = preprocess_inputs(dates, data)
    # Get unique years in input dates.
    years = sorted(set([day.year for day in dates_clean]))
    # Get unique months (YYYY-MM) in input dates.
    year_months = sorted(set([day.strftime("%Y-%m") for day in dates_clean]))

    nrows = int(np.ceil(len(year_months) / ncols))
    if not figsize:
        if ncols == 6:
            figsize = (12, 0.5 + nrows * 2)
        elif ncols == 5:
            figsize = (12, 1 + nrows * 2)
        elif ncols == 4:
            figsize = (14, 2 + nrows * 2)
        elif ncols == 3:
            figsize = (12, 2 + nrows * 2)

    fig, axes = plt.subplots(nrows, ncols, figsize=figsize)

    for i, year_month in enumerate(year_months):
        month = [day for day in dates_clean if day.strftime("%Y-%m") == year_month]
        vals = [
            val
            for day, val in zip(dates_clean, data_clean)
            if day.strftime("%Y-%m") == year_month
        ]
        month_plot(
            month,  # type: ignore
            vals,
            cmap=cmap,
            date_label=date_label,
            value_label=value_label,
            value_format=value_format,
            ax=axes.reshape(-1)[i],
            cal_mode=True,
        )

    for ax in axes.reshape(-1)[len(year_months) :]:
        ax.set_visible(False)

    plt.subplots_adjust(wspace=0.75, hspace=0.5)
    if title:
        plt.suptitle(get_calendar_title(years), fontsize="x-large", y=1.03)

    return axes
