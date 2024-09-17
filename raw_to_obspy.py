import numpy as np
import pandas as pd 
import obspy
import creep_event_picker as cep
import datetime as dt
import matplotlib.pyplot as plt
import inflect
stringify = inflect.engine()
import math
import os


def one_to_five(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 1:
            if tm_diff[i] == 5:
                break
    return i

def one_to_ten(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 1:
            if tm_diff[i] == 10:
                break
    return i

def one_to_thirty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 1:
            if tm_diff[i] == 30:
                break
    return i

def one_to_sixty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 1:
            if tm_diff[i] == 60:
                break
    return i

def five_to_one(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 5:
            if tm_diff[i] == 1:
                break
    return i

def five_to_ten(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 5:
            if tm_diff[i] == 10:
                break
    return i

def five_to_thirty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 5:
            if tm_diff[i] == 30:
                break
    return i

def five_to_sixty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 5:
            if tm_diff[i] == 60:
                break
    return i

def ten_to_one(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 10:
            if tm_diff[i] == 1:
                break
    return i

def ten_to_five(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 10:
            if tm_diff[i] == 5:
                break
    return i

def ten_to_thirty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 10:
            if tm_diff[i] == 30:
                break
    return i

def ten_to_thirty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 10:
            if tm_diff[i] == 60:
                break
    return i

def thirty_to_one(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 30:
            if tm_diff[i] == 1:
                break
    return i

def thirty_to_five(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 30:
            if tm_diff[i] == 5:
                break
    return i

def thirty_to_sixty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] > 30:
            if tm_diff[i] == 60:
                break
    return i

def sixty_to_one(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 60:
            if tm_diff[i] == 1:
                break
    return i

def sixty_to_five(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 60:
            if tm_diff[i] == 5:
                break
    return i

def sixty_to_ten(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 60:
            if tm_diff[i] == 10:
                break
    return i

def sixty_to_thirty(tm_diff):
    for i in range(len(tm_diff)):
        if tm_diff[i] < 60:
            if tm_diff[i] == 30:
                break
    return i

def check_dir(path):
    isExist = os.path.exists(path)
    if not isExist:
        # Create a new directory because it does not exist 
        os.makedirs(path, exist_ok=True)
    return

def interpolate(creeping, period):
    print(period)
    creeping_df = creeping.copy(deep=True)
    creeping_df.Time = creeping_df.Time.dt.round("1min") #round creep times to nearest mins (make evenly spaced)
    creeping_df.Tm = creeping_df.Tm.dt.round("1min")
    creeping_df.set_index('Time',inplace=True) #set index of the dataframe
    creeping_df.drop_duplicates(subset=['Tm'], inplace=True) 
    upsampled = creeping_df.resample('{k}min'.format(k=period)).ffill(1)
    return upsampled

def import_USGS(station,network):
    print(station)
    try:
        tm,creep = cep.import_text('../../../Data/{p}/Raw/{k}_merge.jl'.format(k=station,p=network))
    except FileNotFoundError:
        try:
            tm,creep = cep.import_text('../../../Data/{p}/Raw/{k}.10min-'.format(k=station,p=network))
        except FileNotFoundError:
            tm,creep = cep.import_text('../../../Data/{p}/Raw/{k}_merge-2.jl'.format(k=station,p=network))

    sample_rate =  round((tm[-1]-tm[-2])/dt.timedelta(minutes=1))
    sample_rate_beg = round((tm[1]-tm[0])/dt.timedelta(minutes=1))
    if sample_rate != sample_rate_beg:
        print('warning, sample rate may have changed, consider splitting')
    tm_diff = (tm[1:] - tm[0:-1])/dt.timedelta(minutes=1)
    tm_diff = np.rint(list(tm_diff))
    boolarr = tm_diff <1
    same_time = tm_diff[boolarr] 

    Time = pd.Series(pd.to_datetime(tm)) #convert to pandas series
    creeping = pd.DataFrame({'Time':Time, 'Tm': Time,'Creep':creep}) #create a pandas dataframe 

    if len(same_time) >0:
        print('oh no')   
        datapoint_to_drop = np.where(tm_diff <1)[0][0]
        print(datapoint_to_drop)
        creeping.drop(datapoint_to_drop,inplace=True)
        creeping.reset_index(inplace=True)
        creeping.drop(['index'],axis=1,inplace=True)
        print(creeping.loc[1916590:1916599])
        boolarr_diff = tm_diff >= 1
        tm_diff = tm_diff[boolarr_diff]
    creeping.drop(creeping.loc[creeping.Tm.isnull()].index,inplace=True)
    creeping.reset_index(inplace=True)
    creeping.drop(['index'],axis=1,inplace=True)  
    return creeping, tm_diff

def import_USGS_C46(station,network):
    print(station)
    try:
        tm,creep = cep.import_text('../../../Data/{p}/Raw/c461_10min_11_6_20.txt'.format(k=station,p=network))
    except FileNotFoundError:
        try:
            tm,creep = cep.import_text('../../../Data/{p}/Raw/{k}.10min-'.format(k=station,p=network))
        except FileNotFoundError:
            tm,creep = cep.import_text('../../../Data/{p}/Raw/{k}_merge-2.jl'.format(k=station,p=network))

    sample_rate =  round((tm[-1]-tm[-2])/dt.timedelta(minutes=1))
    sample_rate_beg = round((tm[1]-tm[0])/dt.timedelta(minutes=1))
    if sample_rate != sample_rate_beg:
        print('warning, sample rate may have changed, consider splitting')
    tm_diff = (tm[1:] - tm[0:-1])/dt.timedelta(minutes=1)
    tm_diff = np.rint(list(tm_diff))
    boolarr = tm_diff <1
    same_time = tm_diff[boolarr] 

    Time = pd.Series(pd.to_datetime(tm)) #convert to pandas series
    creeping = pd.DataFrame({'Time':Time, 'Tm': Time,'Creep':creep}) #create a pandas dataframe 

    if len(same_time) >0:
        print('oh no')   
        datapoint_to_drop = np.where(tm_diff <1)[0][0]
        print(datapoint_to_drop)
        creeping.drop(datapoint_to_drop,inplace=True)
        creeping.reset_index(inplace=True)
        creeping.drop(['index'],axis=1,inplace=True)
        print(creeping.loc[1916590:1916599])
        boolarr_diff = tm_diff >= 1
        tm_diff = tm_diff[boolarr_diff]
    creeping.drop(creeping.loc[creeping.Tm.isnull()].index,inplace=True)
    creeping.reset_index(inplace=True)
    creeping.drop(['index'],axis=1,inplace=True)  
    return creeping, tm_diff

def import_csv_roger(station,network):
    df = pd.read_csv('../../../Data/{p}/CSV/{k}.csv'.format(k=station,p=network))
    tm = np.array(pd.to_datetime(df.Date))
    creep = df.Slip

    sample_rate =  round((pd.to_datetime(tm[-1])-pd.to_datetime(tm[-2]))/dt.timedelta(minutes=1))
    sample_rate_beg = round((pd.to_datetime(tm[1])-pd.to_datetime(tm[0]))/dt.timedelta(minutes=1))
    if sample_rate != sample_rate_beg:
        print('warning, sample rate may have changed, consider splitting')
    tm_diff = (pd.to_datetime(tm[1:]) - pd.to_datetime(tm[0:-1]))/dt.timedelta(minutes=1)
    tm_diff = np.rint(list(tm_diff))
    boolarr = tm_diff <1
    same_time = tm_diff[boolarr] 


    Time = pd.Series(pd.to_datetime(tm)) #convert to pandas series
    creeping = pd.DataFrame({'Time':Time, 'Tm': Time,'Creep':creep}) #create a pandas dataframe   
    if len(same_time) >0:
        print('oh no')   
        datapoint_to_drop = np.where(tm_diff <1)[0][0]
        print(datapoint_to_drop)
        creeping.drop(datapoint_to_drop,inplace=True)
        creeping.reset_index(inplace=True)
        creeping.drop(['index'],axis=1,inplace=True)
        print(creeping.loc[1916590:1916599])
        boolarr_diff = tm_diff >= 1
        tm_diff = tm_diff[boolarr_diff]
    creeping.drop(creeping.loc[creeping.Tm.isnull()].index,inplace=True)
    creeping.reset_index(inplace=True)
    creeping.drop(['index'],axis=1,inplace=True)
    return creeping, tm_diff