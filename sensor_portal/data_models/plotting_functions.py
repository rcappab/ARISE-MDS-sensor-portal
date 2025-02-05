from .models import DataFile
from django.db.models import Count, Sum
from datetime import datetime


def get_all_file_metric_dicts(data_files):
    file_dict = get_database_file_metrics(data_files)
    return create_metric_dicts(file_dict, 'recording_dt__date', 'Date')


def get_database_file_metrics(data_files):
    # do aggregation of files per day

    file_dict = data_files.values('recording_dt__date').annotate(
        files_per_day__number_of_files=Count('id'),
        file_volume_per_day__bytes=Sum('file_size')).values(
            'recording_dt__date',
            'files_per_day__number_of_files',
            'file_volume_per_day__bytes')

    file_dict = list(file_dict)
    if len(file_dict) == 0:
        return None

    return file_dict


def create_metric_dicts(file_dict, x_key, x_label):
    x_values = [str(x[x_key]) if type(x) is datetime else x[x_key]
                for x in file_dict]

    metrics = [x for x in file_dict[0].keys() if x != x_key]

    all_metrics_dict = {}

    for metric in metrics:
        metric_name, y_label = metric.split('__')
        y_values = [x[metric] for x in file_dict]
        metric_dict = {"name": metric_name, "x_label": x_label, "y_label": y_label,
                       "x_values": x_values, "y_values": y_values}
        all_metrics_dict[metric_name] = metric_dict

    return all_metrics_dict


def report_file_metrics(data_files):
    data_files = data_files.filter(file_type__name="report")
    # read the csv
