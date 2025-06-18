import os
from datetime import date, datetime
from typing import Any, Dict, List, Optional, Union

import numpy as np
import pandas as pd
from django.db.models import Count, Sum
from django.db.models.query import QuerySet


def get_all_file_metric_dicts(data_files: QuerySet, get_report_metrics: bool = True) -> Dict[str, Dict[str, Any]]:
    """
    Generate a dictionary containing metrics for all files.

    This function aggregates metrics from the database and optionally from report files.

    Args:
        data_files (QuerySet): A Django QuerySet containing file data.
        get_report_metrics (bool): Whether to include metrics from report files. Defaults to True.

    Returns:
        Dict[str, Dict[str, Any]]: A dictionary containing metrics for all files. Each key represents a metric name,
        and the value is a dictionary with details about the metric (e.g., x_values, y_values, labels, plot types).
    """
    all_file_metric_dict = {}

    # Database metrics
    db_file_dict = get_database_file_metrics(data_files)
    if db_file_dict is not None:
        db_file_metric_dict = create_metric_dicts(
            db_file_dict, 'recording_dt__date', 'Date', ["bar", "scatter"]
        )
        all_file_metric_dict.update(db_file_metric_dict)

    if get_report_metrics:
        # Report file metrics
        report_file_metric_dict = report_file_metrics(data_files)
        all_file_metric_dict.update(report_file_metric_dict)

    return all_file_metric_dict


def get_database_file_metrics(data_files: QuerySet) -> Optional[Dict[str, List[Union[date, int]]]]:
    """
    Aggregates metrics from a database query of data files, grouping by recording date.
    Args:
        data_files (QuerySet): A Django QuerySet containing data file records. 
            Each record is expected to have fields `recording_dt__date`, `id`, and `file_size`.
    Returns:
        Optional[Dict[str, List[Union[date, int]]]]: A dictionary containing aggregated metrics 
        if data exists, or `None` if no data is available. The dictionary keys are:
            - 'recording_dt__date': List of unique recording dates.
            - 'files_per_day__number_of_files': List of the number of files recorded per day.
            - 'file_volume_per_day__bytes': List of the total file size (in bytes) recorded per day.
    """
    # do aggregation of files per day

    file_dict = data_files.values('recording_dt__date').order_by('recording_dt__date').annotate(
        files_per_day__number_of_files=Count('id'),
        file_volume_per_day__bytes=Sum('file_size')).values(
            'recording_dt__date',
            'files_per_day__number_of_files',
            'file_volume_per_day__bytes')

    file_dict = list(file_dict)

    if len(file_dict) == 0:
        return None

    file_dict = {k: [current_dict[k]
                     for current_dict in file_dict] for k in file_dict[0]}

    return file_dict


def create_metric_dicts(file_dict: Dict[str, List[Any]],
                        x_key: str,
                        x_label: str,
                        plot_type: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    Create a dictionary of metrics for plotting.

    This function processes a dictionary of file metrics and generates a structured dictionary
    for plotting purposes, including x-values, y-values, labels, and plot types.

    Args:
        file_dict (Dict[str, List[Any]]): A dictionary containing file metrics. Keys represent metric names,
            and values are lists of metric data.
        x_key (str): The key in `file_dict` representing the x-axis values.
        x_label (str): The label for the x-axis.
        plot_type (List[str]): A list of plot types (e.g., "bar", "scatter") to be associated with the metrics.

    Returns:
        Dict[str, Dict[str, Any]]: A dictionary where each key is a metric name, and the value is another dictionary
        containing details about the metric (e.g., x_label, y_label, x_values, y_values, plot_type).
    """
    x_values = [str(x) if isinstance(x, (datetime, pd.Timestamp))
                else x for x in file_dict[x_key]]

    metrics = [x for x in file_dict.keys() if x != x_key]

    all_metrics_dict: Dict[str, Dict[str, Any]] = {}

    for metric in metrics:
        split_metric = metric.split('__')
        if len(split_metric) > 1:
            metric_name, y_label = split_metric
            if y_label == "":
                continue
        else:
            metric_name = metric
            y_label = metric

        y_values = file_dict[metric]
        metric_dict = {
            "name": metric_name,
            "x_label": x_label,
            "y_label": y_label,
            "x_values": x_values,
            "y_values": y_values,
            "plot_type": plot_type,
        }
        all_metrics_dict[metric_name] = metric_dict

    return all_metrics_dict


def report_file_metrics(data_files: QuerySet) -> Dict[str, Dict[str, Any]]:
    """
    Extract metrics from report files and prepare them for plotting.

    This function filters report files from the provided QuerySet, reads their contents,
    processes the data, and generates a dictionary of metrics suitable for plotting.

    Args:
        data_files (QuerySet): A Django QuerySet containing file data. Each record is expected
            to have fields `file_type__name`, `local_storage`, `file_format`, `local_path`, `path`,
            `file_name`, and `file_format`.

    Returns:
        Dict[str, Dict[str, Any]]: A dictionary where each key is a metric name, and the value is another dictionary
        containing details about the metric (e.g., x_label, y_label, x_values, y_values, plot_type).
        Returns an empty dictionary if no valid report files are found or if no datetime columns exist in the data.
    """
    data_files = data_files.filter(
        file_type__name="report", local_storage=True, file_format=".csv"
    )

    if not data_files.exists():
        return {}

    file_path_dicts = list(data_files.values(
        "local_path", "path", "file_name", "file_format"
    ))

    # Read the CSV files into DataFrames
    all_df_list: List[pd.DataFrame] = []
    for file_path_dict in file_path_dicts:
        file_path = os.path.join(
            file_path_dict["local_path"],
            file_path_dict["path"],
            file_path_dict["file_name"] + file_path_dict["file_format"]
        )
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.lower()
        all_df_list.append(df)

    full_df = pd.concat(all_df_list)

    # Attempt to convert columns to datetime if applicable
    full_df = full_df.apply(
        lambda col: pd.to_datetime(col, errors='ignore')
        if col.dtypes == object and 'date' in col.name else col,
        axis=0
    )

    full_df = full_df.convert_dtypes()

    date_time_cols = full_df.select_dtypes(include=[np.datetime64])

    # Assume the first datetime column is the correct one
    date_time_keys = list(date_time_cols.columns.values)

    if len(date_time_keys) == 0:
        return {}

    date_time_key = date_time_keys[0]
    if len(date_time_keys) > 1:
        full_df.drop(columns=date_time_keys[1:], inplace=True)

    full_df = full_df.sort_values(by=date_time_key)

    full_df_numeric = full_df.select_dtypes(include=[np.datetime64, np.number])

    file_dict = full_df_numeric.to_dict(orient="list")

    metric_dict = create_metric_dicts(
        file_dict, date_time_key, "Date", ["scatter"]
    )
    return metric_dict
