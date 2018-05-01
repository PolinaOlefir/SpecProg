import os
from requests import get
from bs4 import BeautifulSoup
from datetime import datetime

class DataLoader(object):
    
    def __init__(self):
        
        self.data_dir = './data'
        self.url = "https://www.star.nesdis.noaa.gov/smcd/emb/vci/VH/get_provinceData.php?country=UKR&provinceID={}&year1={}&year2={}&type=Mean"
        self.filename = "P{:02}-{}.csv"
        
        if not os.path.exists(self.data_dir): # Create the data folder if not exists
            os.makedirs(self.data_dir)
        else: # Clear the data folder if exists
            for name in os.listdir(self.data_dir):
                file_path = os.path.join(self.data_dir, name)
                if os.path.isfile(file_path):
                    os.unlink(file_path)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        return True

    def get_province_data(self, province_id, year_from = 2014, year_to = 2017):

        save_path = os.path.join(self.data_dir, self.filename.format(province_id, datetime.now().strftime("%y%m%d-%H%M%S")))

        # Request data and extract pre-formatted content from the response
        soup = BeautifulSoup(get(self.url.format(province_id, year_from, year_to)).text, 'html.parser')
        pre_content = str(soup.find("pre").contents[0])
        
        # The content has incorrect .csv header, so skip it from file
        csv_content = '\n'.join(line for line in pre_content.splitlines()[1:])
        
        # Save pre-formatted content to .csv file
        with open(save_path,"w") as csv_file:
            csv_file.write(csv_content)
