import pandas as pd

def get_col_list(hyp_params):
    """
    returns a list of lists containing hyper-parameters of XD.
    parameters
    ----------------
    :param: hyp_params (dict) keys: names of hyp_params, values: lists of HP values
    """
    y = []
    for n in range(len(list(hyp_params.keys()))):
        a = []
        x = hyp_params[list(hyp_params.keys())[n]]
        
        if type(x[0]) == tuple:
            x1 = []
            for h in x:
                x1.append(str(h))
            x = x1
        if callable(x[0]):
            a.append([x[s].__name__ for s in range(len(x))])
            y.append(a[0])
        else:
            y.append(x)
    return y

def multi_index_df(index, hyp_params):
    """
    Creates dataframe for storing the mean scores for each hyper-parameter
    for each subject. Mean and Std. of each hyper-parameter is then stored for plotting.
    """
    columns_list = get_col_list(hyp_params)
    columns = list()
    for i in range(len(hyp_params)):
        for j in range(len(hyp_params[list(hyp_params.keys())[i]])):
            columns.append(f'{list(hyp_params.keys())[i]}, {columns_list[i][j]}')
   
    df = pd.DataFrame(index=index, columns=columns)
    a = df.columns.str.split(', ', expand=True).values

    #swap values in NaN and replace NAN to ''
    df.columns = pd.MultiIndex.from_tuples([('', x[0]) if pd.isnull(x[1]) else x for x in a])
    return df