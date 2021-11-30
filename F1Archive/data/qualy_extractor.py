import pandas as pd 
import numpy as np 
import bs4 as bs 
import urllib.request
import logging
from F1Archive.utils import get_col_list, multi_index_df
from F1Archive.data.data_extraction import DataExtractor

logger = logging.getLogger()
logger.setLevel(logging.INFO)
console_handler_Q = logging.StreamHandler()
log_format = '%(asctime)s | %(levelname)s: %(message)s'
console_handler_Q.setFormatter(logging.Formatter(log_format))
logger.addHandler(console_handler_Q)

def get_driver_team_list(df: pd.DataFrame):
    driver_team_list = []
    for n, row in df.iterrows():
        driver_team_list.append(row['Details']['Driver'] + '_' + row['Details']['Car'])
    return driver_team_list


class QualyExtractor(DataExtractor):
    """
    Extract and format qualifying data with DataExtractor as a super class
    """
    def __init__(self):
        super(QualyExtractor, self).__init__()
        self.qualy_urls = dict()
        self.qualy_results = dict()

    def get_qualy_urls(self, return_urls=False):
        """
        Input: YEAR: str OR int
        Output: qualy_urls: list of urls containing qualifing results for specific year
        """
        assert bool(self.year_urls), "get_race_urls() method must be called before get_qualy_urls()" 

        all_urls = []
        for yr, urls in self.year_urls.items():
            qualy_urls = []
            for url in urls:

                source = urllib.request.urlopen(f"{self.HOMEPAGE}{url}").read()
                soup = bs.BeautifulSoup(source,'lxml')
        
                for url in soup.find_all('a'):
                    
                    if 'qualifying-0' in str(url.get('href')) and url.get('href') not in qualy_urls:
                        qualy_urls.append(url.get('href'))
                        
                    elif int(yr) >= 2006 and 'qualifying' in str(url.get('href')) and url.get('href') not in qualy_urls:
                        qualy_urls.append(url.get('href'))
                    # else if 'overallqualifying' in str(url.get('href')) and url.get('href') not in qualy_urls:
                    #     qualy_urls.append(url.get('href')):
            
            self.qualy_urls[yr] = qualy_urls
            all_urls.append(qualy_urls)
        
        if return_urls:
            return all_urls

    def qualy_df(self):
       """
       Method to generate empty dataframe for storing position and points for each race,
       for those years under consideration.
       """
       for yr, urls in self.qualy_urls.items():
            qualy_dict = dict(Details=["Driver", "Car","Driver No"])
            for race in urls:
                if race.split('/')[6] not in qualy_dict.keys():
                    qualy_dict[race.split('/')[6]] = ["Position", "Time", "Team-mate"]
                elif race.split('/')[6]+'A' not in qualy_dict.keys():
                    qualy_dict[race.split('/')[6] + 'A'] = ["Position", "Time", "Team-mate"]
                else:
                    qualy_dict[race.split('/')[6] + 'B'] = ["Position", "Time", "Team-mate"]
            self.qualy_results[yr] = multi_index_df([], qualy_dict)

    def year_qualy_results(self, logging=False):
        """
        """
        if not bool(self.qualy_results):
            self.qualy_df()
        
        for yr, urls in self.qualy_urls.items():
            col_num = 3
            results_df = self.qualy_results[yr]
            
            logger.info(f"Extracting qualifying results for {yr} season")
            placeholder = [0 for i in range(len(urls)*3)]
        
            for n, race in enumerate(urls):
                
                race = f"{self.HOMEPAGE}{race}"
                
                df = self.data_to_table(race, logging=logging)
                df.drop_duplicates(subset='Pos', keep='first', inplace=True) # remove duplicates from F1 site
                
                #display(df.No)
                if n == 0:
                    results_df["Details","Car"] = df["Car"]
                    results_df["Details", "Driver"] = df["Driver"]
                    results_df["Details", 'Driver No'] = df.index
                    results_df.index = df.index
                
                #display(results_df)
                # add previously unseen drivers at each race
                for ind in df.index.difference(results_df.index):
        
                    results_df.loc[ind] = [df['Driver'].loc[ind],df['Car'].loc[ind],ind,*placeholder] #PROBLEM
       
                for n, row in df.iterrows():
                    driver_team = row['Driver'] + '_' + row['Car']
                    if driver_team not in get_driver_team_list(results_df):
                        results_df.loc[1000+n] = [row['Driver'],row['Car'],n,*placeholder]
                

                if int(yr) >= 2006:
                    df['Time'] = self.get_final_qualy(df)
                df['Time'] = df['Time'].fillna(0)

                for ind in df.index:
                    pos = df['Pos'].where(df.index == ind).dropna().values[0]
                    time = df['Time'].where(df.index == ind).dropna().values[0]

                    if df['Car'].loc[ind] == results_df['Details']['Car'].loc[ind]:
                        
                        results_df.at[ind, (f"{results_df.columns[col_num][0]}",'Position')] = pos
                        results_df.at[ind, (f"{results_df.columns[col_num][0]}", 'Time', )] = time
                    else:
                        for i in results_df.index:
                            if results_df['Details']['Driver No'].loc[i] == ind and results_df['Details']['Driver No'].loc[i] != i:
                               
                                results_df.at[i, (f"{results_df.columns[col_num][0]}",'Position')] = pos
                                results_df.at[i, (f"{results_df.columns[col_num][0]}", 'Time', )] = time
        

                col_num += 3
            display(results_df)
            #####Format the dataframe with a few lines#####
            results_df.sort_index(inplace=True)
            #results_df.fillna(0, inplace=True)   
            results_df["Details","Car"] = results_df["Details","Car"].apply(lambda s : s[:3]).map(str.upper) #retain last 3 digits and caps

            self.qualy_results[yr] = results_df

    @staticmethod
    def stack_qualy_results(q_df, race_names=None):
        """
        Stack qualifying results for a single year under the following columns:
        No | Car | Driver | Position | Race | Race No | Team-mate | Time | to_mean
        
        Useful for plotting Qualifying data spread per year.
        Input: q_df (pd.DataFrame) -  Qualifying results dataframe after applying 'qualy_relative_2_mean()'
               race_names (list) - list of race names for given year
        """
        # Establish empty dataframe for stacking race-by-race results
        stacked_df = pd.DataFrame(columns=['No','Driver', 'Car', 'Race', 'Race No',
                                       'Position', 'Time', 'Team-mate', 'to_mean'])
        stacked_df.set_index('No', inplace=True)
        
        for rn, race in enumerate(race_names):
            df_tmp = q_df[race].copy()
            df_tmp["Driver"] = q_df["Details","Driver"]
            df_tmp["Car"] = q_df["Details","Car"]
            df_tmp['Race No'] = [rn+1 for n in range(len(df_tmp.index))]
            r =  [race for n in range(len(df_tmp.index))]
            df_tmp["Race"] = r
            
            stacked_df = pd.concat([stacked_df.copy(), df_tmp.copy()], ignore_index=False, sort=True)
        
        return stacked_df

    @staticmethod
    def get_final_qualy(df):
        """
        Get single qualifying time from three-tied qualifying post 2005
        """
        time = []
        for _, row in df.iterrows():
            
            if not isinstance(row['Q3'], type(np.nan)):
                time.append(row['Q3'])
            elif not isinstance(row['Q2'], type(np.nan)):
                time.append(row['Q2'])
            else:
                time.append(row['Q1'])
        return time
           

if __name__ == '__main__':
    DX = QualyExtractor()
    DX.get_race_urls(1992)
    DX.get_qualy_urls()
    DX.year_qualy_results()
    print(DX.qualy_results['1992'])
