#read_clean_WESM
#%%
import os, sys
import pandas as pd
import numpy as np
import yaml
from functions import *
import warnings
warnings.filterwarnings("ignore")

def main(out_dir, config_file):
    '''
    Location of the parent directory of the csv files from otoole
    '''
    WESM_path = './Ke_WESM_ucl/csv'
    CLEWs_path = './Ke_CLEWs_kth/csv'
    model_merged_path = out_dir
    config_file_path = config_file

    '''
    Read data from both models
    '''
    df_wesm = read_data_csv(WESM_path)
    df_clews = read_data_csv(CLEWs_path)

    '''
    Updating the name of the Region in CLEWs
    '''
    region = df_wesm['REGION'].dropna().unique()[0] 
    df_clews['REGION'] = df_clews['REGION'].replace('RE1', region)

    '''
    Remove parameters and set from the Clews model
    '''
    exclude_params = ['ReserveMargin', 'ReserveMarginTagFuel',
                    'ReserveMarginTagTechnology', 'YearSplit',
                    'YEAR', 'MODE_OF_OPERATION', 'REGION',
                    'CapacityFactor', 'TIMESLICE']
    df_clews = df_clews[~df_clews['PARAM'].isin(exclude_params)]
    df_clews = df_clews[~((df_clews['PARAM'] == 'EMISSION') & (df_clews['VALUE'] == 'CO2'))]

    '''
    Remove common fuels
    '''
    f_wesm = df_wesm[df_wesm['PARAM']=='FUEL']['VALUE']
    f_clews = df_clews[df_clews['PARAM']=='FUEL']['VALUE']
    f_common = f_clews[f_clews.isin(f_wesm)].to_list()
    f_common.append('ELC')
    df_clews = df_clews[~((df_clews['PARAM']=='FUEL') & (df_clews['VALUE'].isin(f_common)))] 

    '''
    Update data
    '''
    # updated IAR fuel from ELC to RESELC
    df_clews.loc[((df_clews['PARAM']=='InputActivityRatio') & (df_clews['FUEL']=='ELC')), 'FUEL'] = 'RESELC'

    #update in tech diesel CLEWS
    df_clews.loc[((df_clews['PARAM']== 'InputActivityRatio') & (df_clews['TECHNOLOGY']=='DEMAGRDSL')), 'FUEL'] = 'AGRDSL'
    vcdiesel= df_clews[(df_clews['PARAM']== 'VariableCost') & (df_clews['TECHNOLOGY']=='DEMAGRDSL')]['VALUE'].unique()[0] 
    df_clews.loc[((df_clews['PARAM']== 'VariableCost') & (df_clews['TECHNOLOGY']=='DEMAGRDSL')), 'VALUE'] = 0.001


    #update in tech diesel WESM IMPDSL
    df_wesm.loc[((df_wesm['PARAM']== 'VariableCost') & (df_wesm['TECHNOLOGY']=='IMPDSL')), 'VALUE'] = 0.001
    tech_diesel = ['FTEAGRDSL', 'FTEINDDSL', 'FTETRADSL']
    df_wesm.loc[((df_wesm['PARAM']== 'VariableCost') & 
                (df_wesm['MODE_OF_OPERATION']==1) & 
                (df_wesm['TECHNOLOGY'].isin(tech_diesel))), 'VALUE'] = vcdiesel


    # remove all other params with fuel 'ELC'
    df_clews = df_clews[~(df_clews['FUEL']=='ELC')]

    '''
    Remove common techs
    '''
    t_wesm = df_wesm[df_wesm['PARAM']=='TECHNOLOGY']['VALUE']
    t_clews = df_clews[df_clews['PARAM']=='TECHNOLOGY']['VALUE']
    t_common = t_clews[t_clews.isin(t_wesm)].to_list()
    t_common.append('IMPELC')

    df_clews = df_clews[~(df_clews['TECHNOLOGY'].isin(t_common))] #techs

    df_clews = df_clews[~((df_clews['PARAM']=='TECHNOLOGY') & (df_clews['VALUE'].isin(t_common)))] #sets
    '''
    Remove demands WESM
    '''
    #cooking demand 
    dem = ['DEMRK1', 'DEMRK2', 'DEMAGR'] #DEMAGR is agriculture
    df_wesm = df_wesm[~(df_wesm['FUEL'].isin(dem))]
    df_wesm = df_wesm[~(df_wesm['TECHNOLOGY'].str.startswith('RK') & pd.notna(df_wesm['TECHNOLOGY']))] # tech
    df_wesm = df_wesm[~((df_wesm['PARAM']=='FUEL') & (df_wesm['VALUE'].isin(dem)))] #sets

    #agricultura demand
    agr_tech = ['AGRDSL001', 'AGRDSL005', 
                'AGRGSL001', 'AGRGSL005', 'AGRHFO001']
    df_wesm = df_wesm[~(df_wesm['TECHNOLOGY'].isin(agr_tech))] #techs
    df_wesm = df_wesm[~((df_wesm['PARAM']=='TECHNOLOGY') & (df_wesm['VALUE'].isin(agr_tech)))] #sets

    '''
    Merge both models 
    '''
    df_merged = pd.concat([df_wesm, df_clews], ignore_index=True)


    '''
    ############################################
    PLOT csv
    ############################################
    '''

    '''
    List of parameters (unique names)
    '''
    param_list = (np.sort(df_merged['PARAM'].unique())).tolist()

    '''
    READ config file .yaml
    '''
    dir_path = os.path.dirname(os.getcwd())
    
    with open(config_file_path, 'r') as file:
        config_file = yaml.safe_load(file)
    config_param_list =[]
    for key in config_file:
        if config_file[key]['type'] == 'param':
            config_param_list.append(key)

    '''
    Create a folder to save csv from the merged model
    '''
    os.makedirs(model_merged_path, exist_ok=True)

    ###
    #Make sure some parameters as dtype 'int', and save a csv file
    ###
    for item in param_list:
        df1 = (df_merged[df_merged['PARAM']==item]).dropna(axis=1)
        #PARAMETERS
        if 'YEAR' in df1.columns:
            df1['YEAR'] = df1['YEAR'].astype(int)
        elif item == 'YEAR':
            df1['VALUE'] = df1['VALUE'].astype(int)

        elif 'DAYTYPE' in df1.columns:
            df1['DAYTYPE'] = df1['DAYTYPE'].astype(int)
        elif item == 'DAYTYPE':
            df1['VALUE'] = df1['VALUE'].astype(int)

        elif 'DAILYTIMEBRACKET' in df1.columns:
            df1['DAILYTIMEBRACKET'] = df1['DAILYTIMEBRACKET'].astype(int)
        elif item == 'DAILYTIMEBRACKET':
            df1['VALUE'] = df1['VALUE'].astype(int)

        elif 'MODE_OF_OPERATION' in df1.columns:
            df1['MODE_OF_OPERATION'] = df1['MODE_OF_OPERATION'].astype(int)
        elif item == 'MODE_OF_OPERATION':
            df1['VALUE'] = df1['VALUE'].astype(int)
           
        #update decimal places
        #elif item == 'SpecifiedDemandProfile':
        #    df1 = SpeDemProf(df1,4)
        #save as csv
        df1.drop('PARAM', axis=1, inplace=True)
        df1.to_csv(os.path.join(model_merged_path, f'{item}.csv'), index=False)

    """
    Print csv files non existent from the .yaml
    """
    for item in config_param_list:
        if item in param_list:
            pass
        else:
            lst = config_file[item]['indices']
            lst.append('VALUE')
            df_lst = pd.DataFrame(lst).T
            df_lst.columns = lst
            df_lst.drop(index=df_lst.index[0], axis=0, inplace=True)
            df_lst.to_csv(os.path.join(model_merged_path, f'{item}.csv'), index=False)
            df_lst.to_csv(os.path.join(model_merged_path, f'{item}.csv'), index=False)

if __name__ == '__main__':
    if len(sys.argv)!= 3:
        msg = "Usage: python {} <out_dir> <config_file>"
        print(msg.format(sys.argv[0]))
        sys.exit(1)
    else:
        out_dir = sys.argv[1]
        config_file = sys.argv[2]
        main(out_dir, config_file)