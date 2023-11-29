import os
import glob
import pandas as pd
import re
import matplotlib.pyplot as plt
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

    pattern = re.compile("00331_(?P<ID>\w+)_00331_(?P<ORIGINAL_ID>\w+)_(?P<EYE>OS|OD)_.*_(?P<PROTOCOL>Cube 12x9|Angio 6x6)")

    match = pattern.match(input_string)

    if match:
        return f"{match.group('ID')}_{match.group('EYE')}_{match.group('PROTOCOL')}", match.group('ORIGINAL_ID'), match.group('EYE'), match.group('PROTOCOL')
    else:
        return None


def prepare_thickness(path, direction):

    folder_list = glob.glob(f'{path}/*/')

    thickness = pd.DataFrame(columns=['Entry', 'Original ID', 'Eye', 'Protocol', 'Region1', 'Region2', 'Region3', 'Region4', 'Region5', 'Region6'])

    for item in folder_list:

        folder_name = item.split('\\')[-2]

        subfolder_path = f'{item}Quantization/*.csv'

        csv_list = glob.glob(subfolder_path)

        thickness_csv = get_latest_file(csv_list)

        thickness_row = pd.read_csv(thickness_csv, sep=',', names=['Region1', 'Region2', 'Region3', 'Region4', 'Region5', 'Region6', 'INVALID'])
        thickness_row = thickness_row.iloc[:, 0:6]

        info, original_id, eye, protocol = extract_info(folder_name)
        thickness_row.insert(0, 'Protocol', protocol)
        thickness_row.insert(0, 'Eye', eye)
        thickness_row.insert(0, 'Original ID', original_id)
        thickness_row.insert(0, 'Entry', info)
        thickness = pd.concat([thickness, thickness_row])

    thickness = thickness.sort_values('Entry').reset_index(drop=True)

    thickness_dic = {'Direction': direction, 'Data': thickness}
    return thickness_dic

def statsDirectionComparison(thickness_list, filters, only_diff):

    for filter in filters:
        thickness0_data_with_info = thickness_list[0]['Data'][(thickness_list[0]['Data']['Eye']==filter['Eye'])&(thickness_list[0]['Data']['Protocol']==filter['Protocol'])]
        thickness1_data_with_info = thickness_list[1]['Data'][(thickness_list[1]['Data']['Eye']==filter['Eye'])&(thickness_list[1]['Data']['Protocol']==filter['Protocol'])]

        # remove columns of info
        thickness0_data = thickness0_data_with_info.drop(['Entry', 'Original ID', 'Eye', 'Protocol'], axis=1)
        thickness1_data = thickness1_data_with_info.drop(['Entry', 'Original ID', 'Eye', 'Protocol'], axis=1)

        thickness0_stats = thickness0_data.describe(percentiles=[]).apply(lambda x:round(x,3))
        thickness1_stats = thickness1_data.describe(percentiles=[]).apply(lambda x: round(x, 3))
        diff_stats = (thickness0_data-thickness1_data).describe(percentiles=[]).apply(lambda x:round(x,3))
        diff_percentage_stats = ((thickness0_data-thickness1_data)/thickness0_data*100).describe(percentiles=[]).apply(lambda x:round(x,3))

        print(f"{filter['Eye']}-{filter['Protocol']}:比较{thickness_list[0]['Direction']}和{thickness_list[1]['Direction']}\n")
        print(f"基于{thickness_list[0]['Direction']}厚度: mm")
        print(thickness0_stats)
        print('\n')
        print(f"基于{thickness_list[1]['Direction']}厚度: mm")
        print(thickness1_stats)
        print('\n')
        print(f"厚度差值({thickness_list[0]['Direction']}-{thickness_list[1]['Direction']}): mm")
        print(diff_stats)
        print('\n')
        print(f"厚度差值百分比 (以{thickness_list[0]['Direction']}厚度为基准): %")
        print(diff_percentage_stats)
        print('\n')

        thinkness0_mean = thickness0_stats.loc['mean'].values
        thickness1_mean = thickness1_stats.loc['mean'].values
        diff = diff_stats.loc['mean'].values

        index = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']

        if only_diff:
            df = pd.DataFrame({f"Diff ({thickness_list[0]['Direction']}-{thickness_list[1]['Direction']})": diff}, index=index)
        else:
            df = pd.DataFrame({f"{thickness_list[0]['Direction']}": thinkness0_mean,
                               f"{thickness_list[1]['Direction']}": thickness1_mean,
                               f"Diff ({thickness_list[0]['Direction']}-{thickness_list[1]['Direction']})": diff},
                              index=index)

        ax = df.plot.bar(rot=0, width=0.8)

        if only_diff:
            plt.ylim([0, 0.4])
        plt.xticks(fontsize=20)
        plt.xlabel('Region',fontsize=20)
        plt.ylabel('Thickness: mm',fontsize=20)
        plt.title(f"{filter['Eye']}-{filter['Protocol']}: Mean",fontsize=30)

        # Add values on top of each bar
        for i, v in enumerate(df.values):
            for j, val in enumerate(v):
                if only_diff:
                    ax.text(i + (j - 1) * 0.15, val + 0.02, str(round(val, 3)), ha='center', va='top', fontsize='20')
                else:
                    ax.text(i + (j - 1) * 0.2, val + 1, str(round(val, 3)), ha='center', va='bottom', fontsize='12')
        plt.show()


def statsProtocolComparison(thickness_dic, filters, only_diff):

    for filter in filters:
        thickness0_data_with_info = thickness_dic['Data'][(thickness_dic['Data']['Eye'] == filter['Eye']) & (
                    thickness_dic['Data']['Protocol'] == 'Angio 6x6')]
        thickness1_data_with_info = thickness_dic['Data'][(thickness_dic['Data']['Eye'] == filter['Eye']) & (
                    thickness_dic['Data']['Protocol'] == 'Cube 12x9')]

        # remove columns of info
        thickness0_data = thickness0_data_with_info.drop(['Entry', 'Original ID', 'Eye', 'Protocol'], axis=1).reset_index(drop=True)
        thickness1_data = thickness1_data_with_info.drop(['Entry', 'Original ID', 'Eye', 'Protocol'], axis=1).reset_index(drop=True)

        thickness0_stats = thickness0_data.describe(percentiles=[]).apply(lambda x:round(x,3))
        thickness1_stats = thickness1_data.describe(percentiles=[]).apply(lambda x: round(x, 3))
        diff_stats = (thickness0_data-thickness1_data).describe(percentiles=[]).apply(lambda x:round(x,3))
        diff_percentage_stats = ((thickness0_data-thickness1_data)/thickness0_data*100).describe(percentiles=[]).apply(lambda x:round(x,3))

        print(f"{filter['Eye']}-{thickness_dic['Direction']}:比较Angio 6x6和Cube 12x9\n")
        print(f"Angio 6x6厚度: mm")
        print(thickness0_stats)
        print('\n')
        print(f"Cube 12x9厚度: mm")
        print(thickness1_stats)
        print('\n')
        print(f"厚度差值(Angio 6x6-Cube 12x9): mm")
        print(diff_stats)
        print('\n')
        print(f"厚度差值百分比 (以Angio 6x6厚度为基准): %")
        print(diff_percentage_stats)
        print('\n')

        thinkness0_mean = thickness0_stats.loc['mean'].values
        thickness1_mean = thickness1_stats.loc['mean'].values
        diff = diff_stats.loc['mean'].values

        index = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']
        if only_diff:
            df = pd.DataFrame({'Diff (Angio 6x6-Cube 12x9)': diff},index=index)
        else:
            df = pd.DataFrame({'Angio 6x6': thinkness0_mean, 'Cube 12x9': thickness1_mean, 'Diff (Angio 6x6-Cube 12x9)': diff}, index=index)
        ax = df.plot.bar(rot=0, width=0.8)

        plt.xticks(fontsize=20)
        plt.xlabel('Region',fontsize=20)
        plt.ylabel('Thickness: mm',fontsize=20)
        plt.title(f"{filter['Eye']}-{thickness_dic['Direction']}: Mean",fontsize=30)

        # Add values on top of each bar
        for i, v in enumerate(df.values):
            for j, val in enumerate(v):
                if only_diff:
                    ax.text(i + (j - 1) * 0.15, val + 0.05, str(round(val, 3)), ha='center', va='top', fontsize='20')
                else:
                    ax.text(i + (j-1) * 0.2, val + 1, str(round(val, 3)), ha='center', va='bottom', fontsize='12')
        plt.show()


path = '../Dataset/GlaucomaThickness'
ascan_path = f'{path}/Export_Ascan'
normal_path = f'{path}/Export_Normal'

ascan_thickness_dic = prepare_thickness(ascan_path, 'Ascan')
normal_thickness_dic = prepare_thickness(normal_path, 'Normal')

# # uncomment to save data to csv
# ascan_thickness_dic['Data'].to_csv('ascan.csv', index=False)
# normal_thickness_dic['Data'].to_csv('normal.csv', index=False)

# Comparison between different methods, the same protocol
# filters = [{'Eye': 'OS', 'Protocol': 'Cube 12x9'}]
filters = [{'Eye': 'OS', 'Protocol': 'Angio 6x6'}, {'Eye': 'OS', 'Protocol': 'Cube 12x9'}]
# filters = [{'Eye': 'OS', 'Protocol': 'Angio 6x6'}, {'Eye': 'OS', 'Protocol': 'Cube 12x9'}, {'Eye': 'OD', 'Protocol': 'Angio 6x6'}, {'Eye': 'OD', 'Protocol': 'Cube 12x9'}]

statsDirectionComparison([ascan_thickness_dic, normal_thickness_dic], filters, True)

# Comparison between different protocols, the same method
filters = [{'Eye': 'OS'}]
# filters = [{'Eye': 'OS'}, {'Eye': 'OD'}]

statsProtocolComparison(ascan_thickness_dic, filters, True)
statsProtocolComparison(normal_thickness_dic, filters, True)
