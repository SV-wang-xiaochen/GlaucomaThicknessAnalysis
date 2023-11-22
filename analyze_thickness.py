import os
import glob
import pandas as pd
import re


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


def prepare_thickness(path):

    folder_list = glob.glob(f'{path}/*/')

    thickness = pd.DataFrame(columns=['Entry', 'Eye', 'Protocol', 'Region1', 'Region2', 'Region3', 'Region4', 'Region5', 'Region6'])

    for item in folder_list:

        folder_name = item.split('\\')[-2]

        subfolder_path = f'{item}Quantization/*.csv'

        csv_list = glob.glob(subfolder_path)

        thickness_csv = get_latest_file(csv_list)

        thickness_row = pd.read_csv(thickness_csv, sep=',', names=['Region1', 'Region2', 'Region3', 'Region4', 'Region5', 'Region6', 'INVALID'])
        thickness_row = thickness_row.iloc[:, 0:6]

        info, eye, protocol = extract_info(folder_name)
        thickness_row.insert(0, 'Protocol', protocol)
        thickness_row.insert(0, 'Eye', eye)
        thickness_row.insert(0, 'Entry', info)
        thickness = pd.concat([thickness, thickness_row])

    thickness = thickness.sort_values('Entry').reset_index(drop=True)

    return thickness

path = '../Dataset/GlaucomaThickness'
ascan_path = f'{path}/Export_Ascan'
normal_path = f'{path}/Export_Normal'

ascan_thickness_with_info = prepare_thickness(ascan_path)
normal_thickness_with_info = prepare_thickness(normal_path)

# remove columns of info
ascan_thickness = ascan_thickness_with_info.drop(['Entry', 'Eye', 'Protocol'], axis=1)
normal_thickness = normal_thickness_with_info.drop(['Entry', 'Eye', 'Protocol'], axis=1)
# print(ascan_thickness)
# print(normal_thickness)
print("统计\n")
print("基于Ascan厚度: mm")
print(ascan_thickness.describe(percentiles=[]))
print('\n')
print("基于法线厚度: mm")
print(normal_thickness.describe(percentiles=[]))
print('\n')
print("两种方法的厚度差值: mm")
print((ascan_thickness-normal_thickness).abs().describe(percentiles=[]))
print('\n')
print("两种方法的厚度差值百分比 (以Ascan厚度为基准): %")
print(((ascan_thickness-normal_thickness)/ascan_thickness*100).abs().describe(percentiles=[]))

# # for c in ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']:
# for c in ['R1']:
#     c1 = thickness_sorted[c].reset_index(drop=True)
#     c2 = thickness_shuffle[c].reset_index(drop=True)
#     diff = c1-c2
#     print(diff)
#     # Calculate mean
#     mean_value = diff.mean()
#
#     # Calculate standard deviation
#     std_deviation = diff.std()
#
#     # Calculate minimum and maximum
#     min_value = diff.min()
#     max_value = diff.max()
#
#     # Calculate other statistics using describe method
#     statistics_summary = diff.describe()
#
#     # Print the results
#     print(f"Mean: {mean_value}")
#     print(f"Standard Deviation: {std_deviation}")
#     print(f"Minimum: {min_value}")
#     print(f"Maximum: {max_value}")
#     print("\nAdditional statistics summary:")
#     print(statistics_summary)