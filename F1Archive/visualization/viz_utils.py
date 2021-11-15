import pandas as pd
import seaborn as sns
import numpy as np

def abbreviations():
    abbrevs = {'south-africa':"SA", 'mexico':"MEX", "brazil":"BRA", "spain":"SPA", "san-marino":"SMA",
              "monaco":"MNO", "canada":"CND", "france":"FRA", "great-britain":"GB", "germany":"GER",
              "hungary":"HUN", "belgium":"BEL", "italy":"ITA", "portugal":"POR", "japan":"JAP", "australia":"AUS",
              "united-states":"USA", "europe":"EUR", "pacific":"PAC", "argentina":"ARG", "luxembourg":"LUX", "austria":"AST"}
    return abbrevs

def team_colors(season):

    palette = None
    if season == '1992':
        palette = dict(MCL='#ff8566', TYR='#ccccff', WIL='#ffff00', BRA='#ff33cc', FOO='#ffe6e6', LOT='#ffffb3',
                        FON='#0066cc', MAR='#00ffff', BEN='#b3e6ff', DAL='#ff4d4d', MIN='#331a00', LIG='#000099',
                        FER='#e62e00', VEN='#cccc00', JOR='#00e600', MOD='#00e673').values()

    return palette

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

def stack_constructor_trends(seasons_df):
    """
    Stack constructors results over multiple years to visualize trends.

    Input DataFrame compiles with constructors_champ.get_seasons_df() with columns:
    Team | Year 1 | Year 2 | ... | Year N

    Returns a DataFrame with columns:
    Points | Team | Year
    """
    stacked_df = pd.DataFrame(columns=['Team', 'Points', 'Year'])
    stacked_df_filled = stacked_df.copy()
    print(stacked_df_filled)
    for _, s in enumerate(seasons_df.columns):
        df_tmp = stacked_df.copy()
        df_tmp['Team'] = seasons_df.index
        df_tmp['Points'] = seasons_df[s].values
        df_tmp['Year'] = [s for i in range(len(seasons_df.index))]
        stacked_df_filled = pd.concat([stacked_df_filled.copy(), df_tmp.copy()], ignore_index=False, sort=True)
        del df_tmp
    return stacked_df_filled.fillna(0)
    

def get_cum_results(seasons_results_df):
    """
    Sums points scored on a race-by-race basis.
    """
    
    cum_results = seasons_results_df['Points'].cumsum(axis=1)
    
    cum_results['Driver'] = seasons_results_df['Details']['Driver']#.apply(lambda s : s[-3:]).map(str.upper)
    cum_results.sort_values(by='australia',ascending=False, inplace=True)
    cum_results.set_index('Driver', inplace=True)
    
    return cum_results

def best_11_cumsum(season_results_df):
    """
    compute cumulative scores based on best 11 results
    """
    
    series = season_results_df.drop(['Details', 'Position'])#.drop(['Driver', 'Car'], axis=1).iloc[0]
   
    best_11_cum = np.array(series[:11].cumsum())
    best_11_S = series[:11].sort_values()
    best_11 = np.array(series[:11].sort_values())
    
    for pts in series[11:]:
        if pts > best_11_S.any():
            best_11 = np.delete(best_11,0)
            best_11 = np.insert(best_11, -1, pts)
            
            best_11_cum = np.insert(best_11_cum, len(best_11_cum), np.array(best_11).cumsum()[-1])
            
        else:
            best_11_cum = np.insert(best_11_cum, len(best_11_cum), best_11_cum[-1])
            
    return best_11_cum

def clean_best_11(cum_11_df, seasons_results_df):
    
    best_11_df = pd.DataFrame(pd.DataFrame(cum_11_df)[0].tolist(), columns=seasons_results_df['Points'].columns)
    best_11_df['Driver'] = seasons_results_df['Details']['Driver'].values
    best_11_df['Driver'] = best_11_df['Driver']#.apply(lambda s : s[-3:]).map(str.upper)
    cols_new = list(best_11_df.columns[-1:]) + list(best_11_df.columns[:-1])
    best_11_df = best_11_df[cols_new]
    best_11_df.sort_values(by='australia',ascending=False, inplace=True)
    best_11_df.set_index('Driver', inplace=True)
    
    return best_11_df