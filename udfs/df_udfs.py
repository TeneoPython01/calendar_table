import pandas as pd
import numpy as np

def make_list(var):
    """
    Convert a variable to a list with one item (the original variable) if it isn't a list already.
    :param var: the variable to check.  if it's already a list, do nothing.  else, put it in a list.
    :return: the variable in a one-item list if it wasnt already a list.
    """
    
    if type(var) is not list:
        var = [ var ]

    return(var)

def addColumnFromGroupbyOperation(df, new_field_name, field_to_groupby, operate_on, operation):
    """
    Add a column to a df through an aggregation (via sum, max, min, count, etc) of another column.
    :param df: dataframe that will have the column added from the groupby operation
    :param new_field_name: name of the field (string) that will be created
    :param field_to_groupby: field (string) or list of fields (list of strings) to use in the groupby
    :param operate_on: field (string) or list of fields (list of strings) that will be aggregated (summed, max'd, min'd, etc.)
    :param operation: the aggregation method (string) such as sum, max, min, etc.
    :return: df with new column added
    """

    fields_list = []
    #fields_list.append(field_to_groupby)

    field_to_groupby = make_list(field_to_groupby)

    for item in field_to_groupby:
        fields_list.append(item)

    fields_list.append(operate_on)

    if operation == 'count':
        df[new_field_name] = df.merge(
            df[fields_list].groupby(field_to_groupby)[operate_on].count().reset_index(),
            how='inner',
            on=field_to_groupby,
            suffixes=('','_r')
            )[operate_on+'_r']
    else:
        
        #operation = operation + '()'
        operation = 'np.'+operation

        df[new_field_name] = df.merge(
            df[fields_list].groupby(field_to_groupby)[operate_on].apply(eval(operation)).reset_index(),
            how='inner',
            on=field_to_groupby,
            suffixes=('','_r')
            )[operate_on+'_r']

    return df


