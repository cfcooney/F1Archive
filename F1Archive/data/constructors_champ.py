import pandas as pd 
import bs4 as bs 
import urllib.request
import logging
from F1Archive.data_transforms.points_map import MapPoints
from F1Archive.data.data_extraction import DataExtractor

class TeamsExtractor(DataExtractor):
    
    def __init__(self, logging=False):
        super(TeamsExtractor, self).__init__()
        self.logging = logging
        self.champ_tables = dict()
        self.seasons_df = pd.DataFrame(columns=['Team'])


    def champ_standings(self, YEARS, max_percentage=True, total_percentage=True):
        """
        Add to 'self.champ_tables' dict a pd.Dataframe for each of the years in YEARS argument. 
        """

        if type(YEARS) != list:
            if type(YEARS) == str or int :
                YEARS = [YEARS]

        fcn = lambda y: str(y) if type(y) == int else y # covert to string if integer

        for year in YEARS:

            url = f"{self.HOMEPAGE}en/results.html/{year}/team.html"

            df = self.scores_2_df(url)

            if total_percentage:
                df = self.percentage_of_total(df)
            
            if max_percentage:
                self.get_race_urls(year)
                
                N_RACES = len(self.year_urls[str(year)])
                
                df = self.percentage_of_max(df, N_RACES, year)
            
            self.champ_tables[str(year)] = df

    @staticmethod
    def scores_2_df(url):
        """
        Return a pd.DataFrame champtionship stadings for years contained within 
        the 'url' argument provided
        """
        results_page = urllib.request.urlopen(url).read()
        race_results = bs.BeautifulSoup(results_page,'lxml')
        
        table = race_results.find_all('table')[0]
        
        df = pd.read_html(str(table), flavor='bs4', header=[0])[0]
       
        try:
            df.drop(["Unnamed: 0","Unnamed: 4"], axis=1, inplace=True)
        except Exception:
            pass
        df.set_index('Pos', inplace=True)

        return df

    @staticmethod
    def percentage_of_total(df):
        """
        Add column to df showing each team's percentage of the total points scores for that season.
        """
        df['% of total'] = df['PTS'].copy().apply(lambda x : round((x /df.copy()['PTS'].sum()) * 100, 2))
        return df

    @staticmethod
    def percentage_of_max(df, n_races, year):
        """
        Add column to df showing each team's percentage of the total points scores for that season.
        """
        
        MP = MapPoints(initial_system=[])
        points = MP.get_points(year)
        max_points = n_races * (points[0] + points[1])
        df['% of max'] = df['PTS'].copy().apply(lambda x : round((x / max_points) * 100, 2))
        return df

    def plot_per_max():
        pass

    def plt_per_total():
        pass

    @staticmethod
    def generic_team_names(t):
        """
        Function for extracting generic team names from more specific season team names
        Too hardcoded - needs improvement
        """
        split_t = t.split(" ")
        
        if (len(split_t) == 1):
            return t
        elif (len(split_t) == 2) and (split_t[0] not in ['AlphaTauri', 'Toro', 'Sauber']):
            return split_t[0]
        elif (len(split_t) > 2) and ((t != 'Alfa Romeo Racing Ferrari') and (t != 'Scuderia Toro Rosso Honda') and (t != 'Force India Mercedes') and (t != 'Force India Sahara') and (t != 'Racing Point BWT Mercedes')):
            name = split_t[0] + ' ' + split_t[1]
            return name
        elif ('Toro Rosso' in t) or ('AlphaTauri' in t):
            return 'Toro Rosso'
        elif ('Force India' in t) or ('Racing Point') in t:
            return 'Force India/RP'
        elif ('Sauber' in t) or ('Alfa') in t:
            return 'Sauber/Alfa'
        else:
            return t

    def get_seasons_df(self, metric='PTS'):
        """
        Returns a DataFrame with columns:
        Team | Year 1 | Year 2 | ... | Year N
        """
        assert self.champ_tables != dict(), f"championship tables must be computed first!"
        self.seasons_df.set_index('Team', inplace=True)
        for year, points in self.champ_tables.items():
            for name in points['Team'].apply(self.generic_team_names):
                self.seasons_df.loc[name,year] = points.loc[points['Team'].apply(self.generic_team_names) == name, metric].iloc[0]
                
        self.seasons_df.fillna(value=0, inplace=True) 
     
if __name__ == '__main__':

    CS = TeamsExtractor()
    CS.champ_standings(['1998','1999','2000'])
    standings = CS.champ_tables['1999']
    print(standings)
