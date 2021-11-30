import pandas as pd 
import numpy as np 
from datetime import datetime, date
import functools
import operator
import itertools
pd.options.mode.chained_assignment = None  # default='warn'

fcn = lambda x: round(x-60.0,3) if not  -15 < x < 15 else x # datetime conversion

def datetime_2_time(series, format='%M:%S.%f'):
    """
    covert 'pandas._libs.tslibs.timestamps.Timestamp' to 'datetime.time'
    """
    time = series.to_pydatetime()
    time = time.strftime(format)
    dt = datetime.strptime(time, format)
    tme = dt.time() # convert to datetime.time
    return tme

def try_get_diff(comb, df, race):
    difference = []
    df_tmp1 = df.copy()
    df_tmp1.loc[:, (race, 'Time')] = pd.to_datetime(df.loc[:,
                                                    (race, 'Time')].copy(),
                                                    format='%M:%S.%f').dt.time
    t1 = datetime.combine(date.min, df_tmp1[race, 'Time'].values[comb[0]])

    t2 = datetime.combine(date.min, df_tmp1[race, 'Time'].values[comb[1]])
    a = t1 - t2
    b = t2 - t1

    a = fcn(divmod(a.total_seconds(), 60)[1])
    b = fcn(divmod(b.total_seconds(), 60)[1])


    difference.append(a)
    difference.append(b)
    return difference

def avg_datetime(series):
    """
    Calculates average time from a pd.Series of datetime objects
    """
    #print(series)
    dt_min = series.min()
 
    deltas = [x-dt_min for x in series]
    avg = dt_min + functools.reduce(operator.add, deltas) / len(deltas)
    
    tme = datetime_2_time(avg)
    
    return tme


# def time_diff(df_tmp, race):
#     """
#     Function for extracting differences between team-mates' qualifying times.
#     Input: df_tmp (pd.DataFrame) - Temporary dataframe containing team-mates results
#            race (str) - name of race for which times are being compared
#     Output: df_tmp (pd.DataFrame) - Temporary dataframe with differences added
#             differences (list) - + and - times for each driver
#     """
    
    
#     difference = []
    
#     try:
#         df_tmp.loc[:, (race, 'Time')] = pd.to_datetime(df_tmp.loc[:, (race, 'Time')].copy(), format='%M:%S.%f').dt.time
#         t1 = datetime.combine(date.min, df_tmp[race, 'Time'].values[0])
#         t2 = datetime.combine(date.min, df_tmp[race, 'Time'].values[1])
#         a = t1 - t2
#         b = t2 - t1
        
#         a = fcn(divmod(a.total_seconds(), 60)[1])
#         b = fcn(divmod(b.total_seconds(), 60)[1])
        
    
#         difference.append(a)
#         difference.append(b)
#     except:
#         difference.append(0)
#         difference.append(0)
    
#     for i, n in enumerate(df_tmp.index):
#         df_tmp.at[n, (race, 'Team-mate')] =  difference[i]
    
#     return df_tmp, difference

def time_diff(df_tmp, race):
    """
    Function for extracting differences between team-mates' qualifying times.
    Input: df_tmp (pd.DataFrame) - Temporary dataframe containing team-mates results
           race (str) - name of race for which times are being compared
    Output: df_tmp (pd.DataFrame) - Temporary dataframe with differences added
            differences (list) - + and - times for each driver
    """
    
    
    difference = []
    i_list = [i for i in range(len(df_tmp[race, 'Time'].values))]
    combinations=list(itertools.combinations(i_list, r=2)) 
 
    for c in combinations:
        try:
            difference = try_get_diff(c, df_tmp.copy(), race)
        except Exception as error:
            #print(error)
            pass

    if not difference:
        difference = [0.0, 0.0]

    flag = 0
    for i, n in enumerate(df_tmp.index):

        if not pd.isna(df_tmp.at[n, (race, 'Time')]):
            
            df_tmp.at[n, (race, 'Team-mate')] = difference[i-flag]
        else:
            flag += 1
            
    return df_tmp, difference

def qualy_differences(qualy_df, race_names):
    """
    Function for adding qualifying differences between team-mates to DataFrame
    Input: df (pd.DataFrame) - Extracted from QualyExtractor
         : race_names (list) list of race names for given year
    Output: df (pd.DataFrame) - QualyExtractor DataFrame with relative times added. 
    """
    
    for make in qualy_df['Details','Car'].unique():
        df_tmp = qualy_df.loc[qualy_df['Details','Car'] == make]
        
        for n, race in enumerate(race_names):
            
#             if 0 in df_tmp[race, 'Time'].values or 'DNF' in df_tmp[race, 'Time'].values:
#                 continue

            df_tmp, diff = time_diff(df_tmp, race)
           
            if diff == [0, 0]:
                print(f"No comparison available for Team: {make} at Race: {race}")
            
            for n, ind in enumerate(df_tmp.index):
            
                gap = df_tmp[race, 'Team-mate'].where(df_tmp.index == ind).values[n]

                qualy_df.at[ind, (race, 'Team-mate')] = float(gap)            
                
    qualy_df.fillna(0, inplace=True)   
    return qualy_df

def qualy_relative_2_mean(q_df, race_names=None, threshold=-10):
    """
    Add each drivers qualifying performance relative to the mean for that race.
    """
    q_df_copy = q_df.copy()
    if race_names == None:
        race_names = q_df_copy.columns.levels[0].values[1:]

    qualy_means = dict()

    for race in race_names:
        results = []
        for i, t in enumerate(q_df_copy[race, 'Time'].values):
            
            # convert untimed types for further processing 
            if type(t) !=str or t == 'DNC' or t == 'DNF' or t == 'DNS':
                t = '00:00.0'
            try:
                time = datetime.strptime(t, '%M:%S.%f')
                results.append(time)
            except:
                results.append(t)

        q_df_copy[race, 'Time'] = results # times converted to datetime format
        q_datetime_df = q_df_copy[race, 'Time'] # times in a separate dataframe

        for ind in q_datetime_df.index:
            if str(q_datetime_df[ind]) == '1900-01-01 00:00:00' or q_datetime_df[ind] == 'DNF':
                q_datetime_df.drop(axis=0, index=ind, inplace=True) # datetimes with zeros removed

        # calculate the mean qualifying time for race
        race_mean = avg_datetime(q_datetime_df) 
        mean = datetime.combine(date.min, race_mean)
        qualy_means[race] = mean

        relative_to_mean = []
        for ind in q_datetime_df.index:

            t_ind = datetime_2_time(q_datetime_df.loc[ind])
            t_ind = datetime.combine(date.min, t_ind)
            to_mean = t_ind - mean
            race_mean = fcn(divmod(to_mean.total_seconds(), 60)[1])
            relative_to_mean.append(race_mean)

            q_df.at[ind, (race,'to_mean')] = race_mean
            q_df[race, 'to_mean'] = q_df[race, 'to_mean'].apply(lambda x: np.nan if x < threshold else x)
    return q_df, qualy_means#


def qualy_season_mean_df(df, race_names=None):
    """
    Return a pd.DataFrame with with qualifying differences between team-mates at each
    race and a mean value to be used for plotting.
    """

    if race_names == None:
        race_names = df.columns.levels[0].values[1:]

    new_df = pd.DataFrame(columns=['Driver','Car'])
    new_df['Driver'] = df['Details', 'Driver']
    new_df['Car'] = df['Details', 'Car']

    for race in race_names:
        new_df[race] = df[race, 'Team-mate']

    new_df['Mean'] = new_df.drop(['Driver','Car'], axis=1).mean(axis=1)

    return new_df
