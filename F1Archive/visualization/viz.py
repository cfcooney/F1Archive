import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
from F1Archive.visualization.viz_utils import abbreviations, team_colors
import logging

logger = logging.getLogger()
logger.setLevel(logging.CRITICAL)

def plot_field_spread(df, race_names, figsize=(12,7), colors=None, ylim=None, year='X', save=False, savefile='', style="darkgrid"):
    """
    Plotting function for qualifying field spread across all races for a given season.
    Requires stacked pd.DataFrame from 'stack_qualy_results()'
    """
    font = {'family' : 'Arial',
        'weight' : 'normal',
        'size'   : 14}
    matplotlib.rc('font', **font)

    sns.set_style(style)

    if ylim == None:
        ylim = max(df['to_mean'].max(), abs(df['to_mean'].min()))
    if colors == None:
        palette = team_colors(year)
    if palette == None:
        palette = sns.husl_palette(len(df['Car'].unique()))
    fig = plt.figure(1, figsize=figsize)

    ax = sns.scatterplot(x="Race No", y="to_mean", data=df, hue="Car", palette=palette) 
    ax.set_xticks(list(set(df['Race No'])))
    lgd = ax.legend(bbox_to_anchor=(1.005, 1.0), loc=2, borderaxespad=0.)
    
    #sns.despine()

    # Format title, ticks and labels
    plt.ylim(np.floor(-ylim), np.ceil(ylim))
    ax.set_xticklabels([abbreviations()[key] for key in race_names])

    ax.set(xlabel='Race', ylabel='Time, relative to mean')
    ax.set_title(f'Qualifying field spread for {year} season')

    if save and savefile != None:
        plt.savefig(savefile, bbox_extra_artists=(lgd,), dpi=300)

    return ax


def plot_teammate_comparison(df, team, race_names, figsize=(12,7), ylim=None, year='X', save=False,
                             savefile='', style="light"):
    """
    Plotting function for team-mate qualifying comparison race-by-race for a given season.
    Requires stacked pd.DataFrame from 'stack_qualy_results()'
    """
    assert team in df['Car'].values, f"'{team}' not in df['Car']"
    
    font = {'family' : 'Arial',
        'weight' : 'normal',
        'size'   : 14}
    matplotlib.rc('font', **font)
    if style == 'light':
        sns.set_style("darkgrid")
    else:
        plt.style.use('dark_background')
    
    fig = plt.figure(1, figsize=figsize)

    ax = sns.barplot(x="Race No", y="Team-mate", data=df.where(df['Car'] == team), hue="Driver", palette=['#ff6666','#4dff4d'],
                     saturation=0.5) 

    if ylim:
        plt.ylim(ylim[0], ylim[1])
    ax.set_xticklabels([abbreviations()[key] for key in race_names])
    ax.set(xlabel='Race', ylabel='Time, relative to team-mate')
    ax.set_title(f'Team-mate qualifying comparison for {year} season')

    lgd = ax.legend(bbox_to_anchor=(1.005, 1.0), loc=2, borderaxespad=0.)

    if save and savefile != None:
        plt.savefig(savefile, bbox_extra_artists=(lgd,), dpi=300)

    return ax

def get_teammate_comparisons(df, race_names, figsize=(12,7), ylim=None, year='X', save=False,
                             savefile='', style="light"):
    """
    Get sns.barplots() for all team-mate comparisions for a given year.
    Outputs: (dict) - key: Car make e.g. 'MCL', value: plot of qualifying comparison
    """
    comparisons = dict()
    for team in df['Car'].unique():
        
        comparisons[team] = plot_teammate_comparison(df, team, race_names, figsize=(12,7), ylim=None,
                                                     year='X', save=False, savefile='', style="light")
    return comparisons

def plot_seasons_comparisons(df, race_names, figsize=(14,7), colors=None, ylim=None, year='X', save=False, savefile='', style="darkgrid"):
    """
    Plotting the average qualifying difference between all team-mates for a season
    """

    font = {'family' : 'Arial',
        'weight' : 'normal',
        'size'   : 10}
    matplotlib.rc('font', **font)

    sns.set_style(style)

    if colors == None:
        palette = team_colors(year)
    if palette == None:
        palette = sns.husl_palette(len(df['Car'].unique()))
    fig = plt.figure(1, figsize=figsize)

    ax = sns.barplot(x="Car", y="Mean", data=df, hue="Car", palette=palette, saturation=0.5) 
    ax.get_legend().remove()

    ax.set_xticklabels([name for name in df['Car'].unique()])

    ax.set(xlabel='Team', ylabel='Mean relative qualifying time')
    ax.set_title(f'Average qualifying difference between team-mates for {year} season')

    if save and savefile != None:
        plt.savefig(savefile, bbox_extra_artists=(lgd,), dpi=300)

    return ax

def plot_per_max(df, figsize=(9,5), colors=None, year='X', save=False, savefile='', style="white", 
                 font = {'family' : 'Arial','weight' : 'normal','size'   : 12}, palette=None):
    
    """
    Plotting function for constructors championship points as a percentage of maximum possible
    """
    
    matplotlib.rc('font', **font)
    sns.set_style(style)
    if palette == None:
        palette = sns.husl_palette(len(df['Team'].unique()))
    
    #fig = plt.figure(1, figsize=figsize)
 
    #ax = sns.barplot(x='Team', y='% of max', data=standings, hue="Team", palette=palette, saturation=0.5)
    ax = df.plot.bar(x='Team', y='% of max', figsize=figsize)
    
    plt.ylim(0, 100)
    ax.set_xticklabels([name[:3] for name in df['Team'].unique()])

    ax.set(xlabel='Team', ylabel='Points as percentage of maximum')
    ax.set_title(f'Points as percentage of maximum for {year} season')
    ax.set(xticks=range(0, 9), xticklabels=[name[:3] for name in df['Team']])
    
    ax.get_legend().remove()
    for bar, color in zip(ax.patches, palette):
        bar.set_width(.3)
        bar.set_color(color)

    return ax

def plot_per_total(df, figsize=(9,5), colors=None, year='X', save=False, savefile='', style="white", 
                 font = {'family' : 'Arial','weight' : 'normal','size'   : 12}, palette=None):
    """
    Plotting function for constructors championship points as a percentage of total points scored
    """
    
    matplotlib.rc('font', **font)
    sns.set_style(style)
    if palette == None:
        palette = sns.husl_palette(len(df['Team'].unique()))
    
    ax = df.plot.bar(x='Team', y='% of total', figsize=figsize)
    
    plt.ylim(0, 100)
    ax.set_xticklabels([name[:3] for name in df['Team'].unique()])

    ax.set(xlabel='Team', ylabel='Points as percentage of total')
    ax.set_title(f'Points as percentage of total for {year} season')
    ax.set(xticks=range(0, 9), xticklabels=[name[:3] for name in df['Team']])
    
    ax.get_legend().remove()
    for bar, color in zip(ax.patches, palette):
        bar.set_width(.3)
        bar.set_color(color)

    return ax

def plot_constructors(df, figsize=(9,5), colors=None, year='X', save=False, savefile='', style="white", 
                 font = {'family' : 'Arial','weight' : 'normal','size'   : 12}, palette=None):
    """
    Plotting function for constructors championship points as a percentage of total points scored
    """

    matplotlib.rc('font', **font)
    sns.set_style(style)
    if palette == None:
        palette = sns.husl_palette(len(df['Team'].unique()))
    
    ax = df.plot.bar(x='Team', y='PTS', figsize=figsize)
    
  
    ax.set_xticklabels([name[:3] for name in df['Team'].unique()])

    ax.set(xlabel='Team', ylabel='Points')
    ax.set_title(f'Constructors championship points for {year} season')
    ax.set(xticks=range(0, 9), xticklabels=[name[:3] for name in df['Team']])
    
    ax.get_legend().remove()
    for bar, color in zip(ax.patches, palette):
        bar.set_width(.3)
        bar.set_color(color)

    return ax

def plot_constructors_trend(df, figsize=(10,6), colors=None, first_year='', second_year='', save=False, savefile='', style="whitegrid", 
                font = {'family' : 'Arial','weight' : 'normal','size'   : 12}, palette=None):
    """
    Plotting function for constructors championship trends over multiple years.
    """

    if (first_year == '') or (second_year == ''):
        first_year = df['Year'].unique()[0]
        second_year = df['Year'].unique()[-1]

    matplotlib.rc('font', **font)
    sns.set_style(style)

    Team_set = set(df['Team'])

    if palette == None:
        palette = sns.husl_palette(len(df['Team'].unique()))

    fig = plt.figure(1, figsize=(10,6))


    plt.figure()
    plt.figure(1, figsize=(10,6))

    for Team, color in zip(Team_set, palette):
        selected_data = df.loc[df['Team'] == Team]
        plt.plot(selected_data['Year'], selected_data['Points'], label=Team, marker='o', color=color)

    plt.ylabel('Percentage of available points')
    plt.xlabel('Season')
    plt.title(f'Percentage of constructors points between {first_year} and {second_year}')
    plt.legend(bbox_to_anchor=(1.01, 0.75))
    
    return plt

def plot_cum_results(cum_df):
    fig = plt.figure(figsize=(14,8))
    #ax = fig.add_subplot(1, 1, 1) 
    sns.set(style='whitegrid')

    cum_df.transpose().plot.line(figsize=(14,8),use_index=False, xlim=(0,cum_df.shape[1]-1)).legend(loc='center left',bbox_to_anchor=(1.0, 0.5))
    plt.xlabel("Races")
    plt.ylabel("Points")

    return plt
