"""
App structure is based on spyre/tutorial/quickstart/stocks_example_no_internet_simple.py

Usage Instruction:
1 Before first run, install Spyre - launch Anaconda Prompt:
1.1 Run: "conda update conda" and confirm;
1.2 Run: "conda install -c conda-forge dataspyre" and confirm.
2 To launch the Spyre app: run this file with Python.
3 To see the Spyre app: with web browser, open URL: "http://localhost:9093"
4 To stop the Spyre app: close or terminate Python.

@author: Polina Olefir https://github.com/PolinaOlefir/SpecProg
"""
from spyre import server
from sys import stdout as out
import pandas as pd
import os
import re

# Зчитування даних із лабораторної роботи 1
def read_province_data(data_dir='../lab1/data', pattern='P[0-9]+-[0-9]+-[0-9]+.csv'):
    
    if not os.path.exists(data_dir): # Exit if the folder does not exist.
        out.write("Folder {} not found!\n".format(data_dir))
        return None
    
    regexp = re.compile(pattern)
    data_frame = pd.DataFrame()
    
    for name in (n for n in os.listdir(data_dir) if regexp.match(n)):
        file_path = os.path.join(data_dir, name)
        if os.path.isfile(file_path):
            out.write("Reading {}... ".format(name))

            # Detect province ID from the file name
            province_id = int(re.search('P([0-9]+)', name).group(1))
            
            # Read province data frame from the file
            province_frame = pd.read_csv(file_path, sep='[, ]+', engine='python', #index_col=[0,1],
                                         names=['Year','Week','SMN','SMT','VCI','TCI','VHI'])
            
            # Add column with province_id
            province_frame['Province'] = province_id
            
            # Append the resulting data frame
            data_frame = data_frame.append(province_frame)
            
            out.write("Province ID: {}\n".format(province_id))
    
    return data_frame

# Створити веб-додаток із використанням модуля Spyre, який дозволить:
class VegetationHealthApp(server.App):
    title = "Vegetation Health Time Series"

    # Read list of provinces from lab1:
    provinces = pd.read_csv('../lab1/ukr_provinces.csv', comment='#', sep='[, ]+', engine='python')
    # Prepare selectable options for provinces in "Province" input:
    province_options = [{'label':row['province_name'],'value':row['provinceID']} for index,row in provinces.iterrows()]
    # Prepare selectable options for weeks in "Week ..." inputs:
    week_options = [{'label':i,'value':i} for i in range(1,53,1)]

    inputs = [{
    # обрати часовий ряд VCI, TCI, VHI для набору даних із лабораторної роботи 1 (випадаючий список);
        "type": 'dropdown',
        "label": 'Series',
        "options": [
            {"label": "Vegetation Health Index", "value": "VHI"},
            {"label": "Vegetation Condition Index", "value": "VCI"},
            {"label": "Thermal Condition Index", "value": "TCI"}
        ],
        "value": 'VHI',
        "key": 'series',
        "action_id": "update_data"        
    }, {
    # Вибрати область, для якої буде виконуватись аналіз (випадаючий список);
        "type": 'dropdown',
        "label": 'Province',
        "options": province_options,
        "value": '11',
        "key": 'province',
        "action_id": "update_data"
    }, {
    # Зазначити інтервал тижнів, за які відбираються дані (від);
        "type": 'dropdown',
        "label": 'Week from',
        "options": week_options,
        "value": '1',
        "key": 'week_from',
        "action_id": "update_data"
    }, {
    # Зазначити інтервал тижнів, за які відбираються дані (до);
        "type": 'dropdown',
        "label": 'Week to',
        "options": week_options,
        "value": '52',
        "key": 'week_to',
        "action_id": "update_data"
    }]

    controls = [{
        "type": "hidden",
        "id": "update_data"
    }]

    # Створити кілька вкладок для відображення таблиці із даними на графіку ходу індексів;    
    tabs = ["Plot", "Table"]

    outputs = [{
        "type": "plot",
        "id": "plot",
        "control_id": "update_data",
        "tab": "Plot"
    }, {
        "type": "table",
        "id": "table_id",
        "control_id": "update_data",
        "tab": "Table",
        "on_page_load": True
    }]

    def getData(self, params):
        series = params['series']
        # Note int() conversion, without it comparators (== >= <=) fail.
        province = int(params['province'])
        week_from = int(params['week_from'])
        week_to = int(params['week_to'])
        
        data_frame = read_province_data()
        result_frame = data_frame.loc[(data_frame['Province'] == province)
                                      & (data_frame['Week'] >= week_from)
                                      & (data_frame['Week'] <= week_to),
                                      ['Year', 'Week', series]]
        return result_frame

    def getPlot(self, params):
        series = params['series']
        province = int(params['province'])
        
        # Define province_name by province id:
        province_name = self.provinces.loc[(self.provinces['provinceID'] == province)].iat[0,7]
        
        df = self.getData(params)
        plt_obj = df.set_index(['Year', 'Week']).plot(figsize=(20,10))
        plt_obj.set_ylabel(series)
        plt_obj.set_title(province_name)
        fig = plt_obj.get_figure()
        return fig

if __name__ == '__main__':
    app = VegetationHealthApp()
    app.launch(port=9093)