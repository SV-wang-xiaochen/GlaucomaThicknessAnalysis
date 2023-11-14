import os
import glob
import pandas

def get_latest_file(file_path_list):

    latest_file_index = 0
    lasest_time = os.path.getmtime(file_path_list[latest_file_index])

    for i, file_path in enumerate(file_path_list):
        last_edit_time = os.path.getmtime(file_path)
        if last_edit_time>lasest_time:
            latest_file_index = i

    return file_path_list[latest_file_index]


path = r'..\Dataset\GlaucomaThickness\Export'
folder_list = glob.glob(f'{path}/*/')

for item in folder_list[0:1]:
    print(f'folder name: {item}')
    subfolder_path = f'{item}Quantization'

    csv_list = glob.glob(f'{subfolder_path}/*.csv')

    thickness_csv = get_latest_file(csv_list)
    print(f'lastest csv: {thickness_csv}')
    print('\n')

    thickness = pandas.read_csv(thickness_csv, sep=',', names=['R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'INVALID'])
    thickness = thickness.iloc[:, 0:6]
    print(thickness)