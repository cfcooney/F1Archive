import pandas as pd 
import numpy as np 
import bs4 as bs 
import urllib.request
import logging
from F1Archive.utils import get_col_list, multi_index_df
import os
import random

os.environ['NUMEXPR_MAX_THREADS'] = '4'

    
logger = logging.getLogger()
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
log_format = '%(asctime)s | %(levelname)s: %(message)s'
console_handler.setFormatter(logging.Formatter(log_format))
logger.addHandler(console_handler)


class DataExtractor():

    def __init__(self):
        self.HOMEPAGE = 'https://www.formula1.com/'
        self.year_urls = dict()
        self.year_results = dict()
        # put years/YEARS into constructor

    def change_homepage(self, homepage):
        self.HOMEPAGE = homepage

    def get_race_urls(self, YEARS, return_urls=False):
        """
        Input: YEAR: str OR int
        Output: race_urls: list of urls containing race results for specific year
        """
        all_urls = []
        if type(YEARS) != list:
            if type(YEARS) == str or int :
                YEARS = [YEARS]

        fcn = lambda y: str(y) if type(y) == int else y # covert to string if integer
   
        for year in YEARS:

            year = fcn(year)
            race_urls = []
            source = urllib.request.urlopen(f"https://www.formula1.com/en/results.html/{year}/races.html").read()
            soup = bs.BeautifulSoup(source,'lxml')
      
            for url in soup.find_all('a'):
                if year in str(url.get('href')) and 'race-result' in str(url.get('href')) and url.get('href') not in race_urls:
                    race_urls.append(url.get('href'))
            self.year_urls[year] =  race_urls
            all_urls.append(race_urls)
        
        if return_urls:
            return all_urls

        
    def pos_points_df(self):
       """
       Method to generate empty dataframe for storing position and points for each race,
       for those years under consideration.
       """
       for yr, urls in self.year_urls.items():
            race_names = []
            for race in urls:
                race_names.append(race.split('/')[6])
           
            race_pos_pts = dict(Details=["Driver","Car"], Position=race_names, Points=race_names)
            self.year_results[yr] = multi_index_df([], race_pos_pts)

    @staticmethod
    def data_to_table(url, logging=False):

        race_name = url.split('/')[9]

        if logging:
            logger.info(f"Race: {race_name}")

        results_page = urllib.request.urlopen(url).read()
        race_results = bs.BeautifulSoup(results_page,'lxml')

        table = race_results.find_all('table')[0]
        df = pd.read_html(str(table), flavor='bs4', header=[0])[0]
      
        df.set_index('No', inplace=True)
        try:
            df.drop(["Unnamed: 0","Unnamed: 8"], axis=1, inplace=True)
        except:
            try:
                df.drop(["Unnamed: 0","Unnamed: 6"], axis=1, inplace=True)
            except:
                pass

        return df


    def seasons_results(self, logging=False, return_results=False, print_dataframes=False):
        """
        Extract data from F1 webpage and insert into pd.DataFrame containing driver, car, race position and 
        race points for that season.
        """
        
        if not bool(self.year_results):
            self.pos_points_df()

        for yr, urls in self.year_urls.items():

            #assert bool(self.year_results.get(yr)), f"Results dataframe for {yr} had not been instantiated!"
            results_df = self.year_results[yr]
            df1 = results_df.copy()
            logger.info(f"Extracting results for {yr} season")
            placeholder = [0 for i in range(len(urls)*2)]
            for n, race in enumerate(urls):
                
                race = f"{self.HOMEPAGE}{race}"
                
                df = self.data_to_table(race, logging=True)
                df.index = df['Driver'].apply(lambda s : s[:-3]) #added

                
                if True in df.index.duplicated():#added
                    new_idx = []
                    for i, dup in zip(df.index, df.index.duplicated()):

                        if not dup:
                            new_idx.append(i)
                        else:
                            new_idx.append(i + str(random.randint(1, 100))) #workaround for duplicates
                    df.set_index(pd.Index(new_idx), inplace=True)
                
                if n == 0:
                    results_df["Details","Car"] = df["Car"]
                    results_df["Details", "Driver"] = df["Driver"]
                    results_df.index = df.index
                
                # add previously unseen drivers at each race
                for ind in df.index.difference(results_df.index):

                    results_df.loc[ind] = [df['Driver'].loc[ind],df['Car'].loc[ind],*placeholder]
                
                for ind in df.index:
                    pos = df['Pos'].where(df.index == ind).dropna().values[0]
                    pts = df['PTS'].where(df.index == ind).dropna().values[0]
                    
                    results_df.at[ind, ('Position', f"{race.split('/')[9]}")] = pos
                    results_df.at[ind, ('Points', f"{race.split('/')[9]}")] = pts
                df2=results_df.copy()
            #####Format the dataframe with a few lines#####
            results_df.reset_index(inplace=True)
            
            #results_df.drop(['Driver'], axis=1, inplace=True)
            results_df.fillna(0, inplace=True) 
            #return results_df
            try:
                results_df["Details","Car"] = results_df["Details","Car"].apply(lambda s : s[:3]).map(str.upper) #retain last 3 digits and caps
            except:
                pass
            df3 = results_df.copy()
            self.year_results[yr] = results_df
            if print_dataframes:
                print(results_df.head())
        # return df1, df2, df3
        if return_results:
            return self.year_results

if __name__ == '__main__':
    pass