import os
import glob
import pandas as pd
import re
import numpy as np

def get_latest_file(file_path_list):

    latest_file_index = 0
    lasest_time = os.path.getmtime(file_path_list[latest_file_index])

    for i, file_path in enumerate(file_path_list):
        last_edit_time = os.path.getmtime(file_path)
        if last_edit_time>lasest_time:
            latest_file_index = i

    return file_path_list[latest_file_index]


def extract_info(input_string):
    pattern = re.compile("00331_(?P<ID>\w+)_00331_.*_(?P<EYE>OS|OD)_.*_(?P<PROTOCOL>Cube 12x9|Angio 6x6)")

    match = pattern.match(input_string)

    if match:
        return f"{match.group('ID')}_{match.group('EYE')}_{match.group('PROTOCOL')}", match.group('EYE'), match.group('PROTOCOL')
    else:
        return None


path = r'..\Dataset\GlaucomaThickness\Export_20231120'
folder_list = glob.glob(f'{path}/*/')

thickness = pd.DataFrame(columns=['Entry', 'Eye', 'Protocol', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6'])

for item in folder_list[:10]:

    folder_name = item.split('\\')[-2]
    print(f'folder name: {folder_name}')

    subfolder_path = f'{item}Quantization/*.csv'

    csv_list = glob.glob(subfolder_path)

    thickness_csv = get_latest_file(csv_list)
    print(f'lastest csv: {thickness_csv}')
    print('\n')

    thickness_row = pd.read_csv(thickness_csv, sep=',', names=['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'INVALID'])
    thickness_row = thickness_row.iloc[:, 0:6]

    info, eye, protocol = extract_info(folder_name)
    thickness_row.insert(0, 'Protocol', protocol)
    thickness_row.insert(0, 'Eye', eye)
    thickness_row.insert(0, 'Entry', info)
    thickness = pd.concat([thickness, thickness_row])

thickness = thickness.reset_index(drop=True)
print(thickness)

thickness_sorted = thickness.sort_values('Entry')
# print(thickness_sorted)

thickness_shuffle = thickness.sample(frac=1)
# print(thickness_shuffle)

# a = thickness_sorted.drop(['Entry', 'Eye', 'Protocol'], axis=1)
# b = thickness_shuffle.drop(['Entry', 'Eye', 'Protocol'], axis=1)

# # for c in ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']:
for c in ['R1']:
    c1 = thickness_sorted[c].reset_index(drop=True)
    c2 = thickness_shuffle[c].reset_index(drop=True)
    diff = c1-c2
    print(diff)
    # Calculate mean
    mean_value = diff.mean()

    # Calculate standard deviation
    std_deviation = diff.std()

    # Calculate minimum and maximum
    min_value = diff.min()
    max_value = diff.max()

    # Calculate other statistics using describe method
    statistics_summary = diff.describe()

    # Print the results
    print(f"Mean: {mean_value}")
    print(f"Standard Deviation: {std_deviation}")
    print(f"Minimum: {min_value}")
    print(f"Maximum: {max_value}")
    print("\nAdditional statistics summary:")
    print(statistics_summary)