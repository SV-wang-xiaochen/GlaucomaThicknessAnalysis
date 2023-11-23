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

def stats(ascan_thickness, normal_thickness, filter):

    # remove columns of info
    ascan_thickness = ascan_thickness.drop(['Entry', 'Eye', 'Protocol'], axis=1)
    normal_thickness = normal_thickness.drop(['Entry', 'Eye', 'Protocol'], axis=1)

    print(f"统计-{filter['Eye']}-{filter['Protocol']}\n")
    print("基于Ascan厚度: mm")
    print(ascan_thickness.describe(percentiles=[]).apply(lambda x:round(x,3)))
    print('\n')
    print("基于法线厚度: mm")
    print(normal_thickness.describe(percentiles=[]).apply(lambda x:round(x,3)))
    print('\n')
    print("厚度差值(Ascan-法线): mm")
    print((ascan_thickness-normal_thickness).describe(percentiles=[]).apply(lambda x:round(x,3)))
    print('\n')
    print("厚度差值百分比 (以Ascan厚度为基准): %")
    print(((ascan_thickness-normal_thickness)/ascan_thickness*100).describe(percentiles=[]).apply(lambda x:round(x,3)))
    print('\n')
    # print(ascan_thickness.describe(percentiles=[])['mean'])

path = '../Dataset/GlaucomaThickness'
ascan_path = f'{path}/Export_Ascan'
normal_path = f'{path}/Export_Normal'

ascan_thickness_with_info = prepare_thickness(ascan_path)
normal_thickness_with_info = prepare_thickness(normal_path)

# filters = [{'Eye': 'OS', 'Protocol': 'Angio 6x6'}]
# filters = [{'Eye': 'OS', 'Protocol': 'Angio 6x6'}, {'Eye': 'OS', 'Protocol': 'Cube 12x9'}]
filters = [{'Eye': 'OS', 'Protocol': 'Angio 6x6'}, {'Eye': 'OS', 'Protocol': 'Cube 12x9'}, {'Eye': 'OD', 'Protocol': 'Angio 6x6'}, {'Eye': 'OD', 'Protocol': 'Cube 12x9'}]
for filter in filters:
    ascan_thickness = ascan_thickness_with_info[(ascan_thickness_with_info['Eye']==filter['Eye'])&(ascan_thickness_with_info['Protocol']==filter['Protocol'])]
    normal_thickness = normal_thickness_with_info[(normal_thickness_with_info['Eye']==filter['Eye'])&(normal_thickness_with_info['Protocol']==filter['Protocol'])]
    stats(ascan_thickness,normal_thickness,filter)


angio_mean = [2, 8, 70, 1.5, 25, 12]
cube_mean = [0.1, 17.5, 40, 48, 52, 69]
diff = list(np.array(angio_mean) - np.array(cube_mean))

index = ['R1', 'R2', 'R3', 'R4', 'R5', 'R6']
df = pd.DataFrame({'OS-Angio 6×6': angio_mean, 'OS-Cube 12×9': cube_mean, 'Diff (Angio-Cube)': diff}, index=index)
ax = df.plot.bar(rot=0, width=0.8)

plt.xticks(fontsize=20)
plt.xlabel('Region',fontsize=20)
plt.ylabel('Thickness: mm',fontsize=20)
plt.title('Mean',fontsize=30)

# Add values on top of each bar
for i, v in enumerate(df.values):
    for j, val in enumerate(v):
        ax.text(i + (j-1) * 0.2, val + 1, str(round(val, 3)), ha='center', va='bottom')

plt.show()
