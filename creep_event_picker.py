import numpy as np
import pandas as pd
import datetime as dt
import scipy
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

def picker(path,file_type):

    # import raw data files as txt or csv and calculate sample rate
    print('importing data')
    if file_type == 'txt':
        tm, creep = import_text(path)
        sample_rate =  round((tm[-1]-tm[-2])/dt.timedelta(minutes=1)) #identify the sampling frequency of the data
        sample_rate_beg = round((tm[1]-tm[0])/dt.timedelta(minutes=1))

    elif file_type == 'csv':
        tm, creep = import_csv(path)
        tm = pd.to_datetime(tm)
        sample_rate =  round((tm.iloc[-1]-tm.iloc[-2])/dt.timedelta(minutes=1)) #identify the sampling frequency of the data
        sample_rate_beg = round((tm.iloc[1]-tm.iloc[0])/dt.timedelta(minutes=1))

    
    # interpolate data
    print('interpolating')
    tm = pd.to_datetime(tm)
    tm_int, creep_int, upsampled = interpolate(tm,creep,sample_rate,sample_rate_beg)
    print('calculating daily and hourly offsets')
    # calculate daily and hourly average slips
    Daily_slip = slip_difference(sample_rate,[tm_int,creep_int],'day')
    Hourly_slip = slip_difference(sample_rate,[tm_int,creep_int],'hour')
    # detrend the data
    print('detrend and filter')
    creep_DT = scipy.signal.detrend(creep_int)
    # filter the data
    upper_freq=input("longer duration for bandpass filtering in mins, e.g., 5 days = 7200")
    lower_freq=input("shorter duration for bandpass filtering in mins, e.g., 2 hrs =  120")
    sos = scipy.signal.butter(4,[1/int(upper_freq),1/int(lower_freq)], 'band',output = 'sos',fs=0.10) #bandpass filter for 2hrs and 5days
    creep_data  = scipy.signal.sosfiltfilt(sos,creep_DT) # filter the data
    # extract template event
    print('extracting template')
    template_event = template_finder(tm_int,creep_int)
    

    START = pd.to_datetime(template_event.Start_Time.iloc[0]) #extract start time
    END = pd.to_datetime(template_event.End_Time.iloc[0]) # extract end time

    boolarr = (START.replace(tzinfo=None)<= tm_int) & (tm_int <= END.replace(tzinfo=None)) #create boolean for the timing of the template
    Time = tm_int[boolarr] #extract timeing of template
    Creep = creep_data[boolarr] #template
    plt.close('all')
    #run cross correlation
    print('running cross correlation')
    x_corr = X_corr(creep_data,Creep,tm_int)

    w_T = np.array(x_corr.x_corr,dtype = float) #extract w_T
    t_w_T = pd.Series(np.array(x_corr.TWT)) #extract timeings
    t_w_T = pd.to_datetime(t_w_T)
    v = np.array(x_corr.V) #extract creep record
    X_corr_plot(w_T)

    # make daily slip and w_t the same length
    Daily_slip = np.array(Daily_slip)
    TWT_DS = t_w_T[0:(len(tm_int)-143)]
    w_T_DS = w_T[0:(len(tm_int)-143)]
    Daily_slip_WT = Daily_slip[0:-(len(Creep)-145)]

    #tuning parameters
    print('enter tuning parameters for noise level')
    X_Corr_peaks_width = input("width of x_cor peaks, default 6")
    x_corr_peaks(w_T_DS, X_Corr_peaks_width, Daily_slip)

    X_Corr_peaks_WT = input("height of x_cor peaks i.e., cut off threshold, default 0.8")

    A,properties = scipy.signal.find_peaks(w_T,height=float(X_Corr_peaks_WT),width = float(X_Corr_peaks_width)) #find peaks above threshold value that are an hour long
    EVENT = w_T[0:][A]
    EVENT_TIME = t_w_T.iloc[A]
    EVENT_CREEP = v[0:][A]
    peak_wt = pd.DataFrame({'Time':EVENT_TIME,'Creep':EVENT_CREEP,'w_T':EVENT})
    
    DS_Cut_Per = input("percentile of daily slip for defining end, default 95")
    Troughs_width = input("Trough widths, defualt 6")
    Troughs_distance = input("Trough distances, defualt 12")

    print('finalising catalogue of picks... please wait')
    DS_Cut = np.percentile(Daily_slip,float(DS_Cut_Per))#this calculates the 95th percentile of the peak Daily_slip value, should be creeping above this


    newindex = np.arange(0,len(peak_wt),1)
    peak_WT_new = peak_wt.set_index(newindex) #reindex creep events to allow for for loop

    # extract start time more accurately and estimate end time, duraiton and slip
    Picked_Creep = pd.DataFrame.copy(peak_WT_new, deep=True) 
    Picked_Creep = start_and_end_times(tm_int,creep_int,Hourly_slip,Picked_Creep,TWT_DS,Daily_slip_WT, DS_Cut,Troughs_width,Troughs_distance,creep_data)
    
    #Clean up picks
    Cleaned_picks = picks_clean(Picked_Creep)
    return Cleaned_picks
'''
    # flag events with beginnings or ends in interpolated sections
    Final_picks = warnings_interp(upsampled,Picked_Creep)#Cleaned_picks)
    Final_picks['Pick_diff'] = pd.to_datetime(Final_picks.Start_Time) - pd.to_datetime(Final_picks.Time_Trough)
    print(Final_picks)

    # manual checking
    print('begin manual checks: {k} events'.format(k=len(Final_picks)))
    Checked_final_picks = manual_check(Final_picks,tm,creep)

    # adjust end times of subevents
    all_events_sub_events = sub_event(Checked_final_picks,tm,creep)
    return all_events_sub_events
'''
def sub_event(df,tm,creep):

    for i in range(len(df)):
        if df.Event_rating.iloc[i] == 'First or sub event':
            df.End_Time.iloc[i] == df.Start_Time.iloc[i+1]
            boolarr = tm >= df.Start_Time.iloc[i] & tm<= df.End_Time.iloc[i]
            slip = creep[boolarr]
            time = tm[boolarr]
            event_slip = slip[-1] - slip[0]
            df.End_offset.iloc[i] = slip[-1]
            df.Start_offset.iloc[i] = slip[0]
            df.duraiton = (df.End_Time - df.Start_Time)
    return


def manual_check(Final_picks,tm, creep):
    good_event = []
    for i in range(len(Final_picks)):
        boolarr = (Final_picks.Time_Trough.iloc[i] >= tm) & (tm <= Final_picks.End_Time.iloc[i])
        event_time = tm[boolarr]
        event_slip = creep[boolarr]
        if Final_picks.False_P.iloc[i] == 2:
            color = 'red'
            linestyle = '-.'
        elif Final_picks.False_P.iloc[i] == 1:
            color = 'orange'
            linestyle = '--'
        else:
            color = 'green'
            linestyle = '-'

        fig=plt.figure()
        ax = plt.subplot(1,1,1)#, xlim=(0,1), ylim=(0,1), autoscale_on=False)
        ax.plot(event_time, event_slip, color=color, linestyle=linestyle)
        ax.scatter(Final_picks.Time_Trough.iloc[i],Final_picks.Creep_Trough.iloc[i])
        ax.scatter(Final_picks.Start_Time.iloc[i],Final_picks.Start_Displacement.iloc[i],marker='x')
        ax.scatter(Final_picks.End_Time.iloc[i],Final_picks.End_Displacement.iloc[i],marker='d')

        scale = 1.1
        zp = ZoomPan()
        figZoom = zp.zoom_factory(ax, base_scale = scale)
        figPan = zp.pan_factory(ax)
        plt.title('2 clicks for first or sub event, 1 click for single or final event/n and press esc for non events')
        s = 1
        plt.show()
        pts = plt.ginput(2,timeout = -1)
        plt.close()
        #print(pts)

        Coords_creep=[]
        Creep_identified=[]
        for sublist in pts:
            for item in sublist:
                Coords_creep.append(item)
        Creep_identified = [Coords_creep]

        if len(Creep_identified) == 2:
            good_event.append('First or sub event')
        elif len(Creep_identified) ==1:
            good_event.append('Single or Final event')        
        else:
            good_event.append(0)

    Final_picks['Event_rating'] = good_event

    return Final_picks




def warnings_interp(upsampled,Picked_Creep):
    print('running?')
    index_NAN = upsampled['Creep'].index[upsampled['Creep'].apply(np.isnan)]
    False_Time = upsampled['Time'].loc[index_NAN[:]]
    FALSE_S = Picked_Creep.Start_Time.isin(False_Time).astype(int)
    FALSE_E = Picked_Creep.End_Time.isin(False_Time).astype(int)
    FALSE_P = FALSE_S + FALSE_E
    #print(FALSE_P)
    Picked_Creep['False_P'] = FALSE_P 
    Picked_Creep.reset_index(inplace=True)
    #Picked_Creep.drop(Picked_Creep[Picked_Creep['False_P']!=0].index,inplace=True)
    #index_final = np.arange(0,len(Picked_Creep),1)
    #Picked_Final = Picked_Creep.set_index(index_final)
    #print(Picked_Creep)
    return Picked_Creep

def picks_clean(Picked_Creep):
    # removes instantaneous offsets

    Picked_Creep.drop(Picked_Creep[(Picked_Creep['Dur']/dt.timedelta(minutes=1))<=10].index,inplace=True)
    newindex = np.arange(0,len(Picked_Creep),1)
    Picked_Creep = Picked_Creep.set_index(newindex)
    #print(len(Picked_Creep))
    
    #removes very small events

    '''TSCUT = Picked_Creep.Total_Slip
    TSCUT2 = np.sort(TSCUT)[::-1]
    top_5_percent = round(len(TSCUT2)/100)
    TS5_Max = TSCUT2[:top_5_percent]
    Creep_Cut = 0.01*np.median(TS5_Max) #create cut off at 1% of the median of the max 1% total slips
    indexNames = Picked_Creep[Picked_Creep['Total_Slip'] <= Creep_Cut].index #possibly need to add a different discriminant here
    Picked_Creep.drop(indexNames , inplace=True)
    newindex = np.arange(0,len(Picked_Creep),1)
    Picked_Creep = Picked_Creep.set_index(newindex) #reindex creep events to allow for for loop'''

    # drop duplicates
    #Picked_Creep.drop_duplicates(subset=['Time_Trough'], inplace=True)
    #Picked_Creep.drop_duplicates(subset=['End_Time'], inplace=True) 
    #removes duplicates
    newindex = np.arange(0,len(Picked_Creep),1)
    Picked_Creep = Picked_Creep.set_index(newindex)
    #print(len(Picked_Creep))

    return Picked_Creep


def start_and_end_times(tm_int,creep_int,Hourly_slip,Picked,TWT_DS,Daily_slip_WT, DS_Cut,Troughs_width,Troughs_distance,creep_data):

    tm_HS = tm_int[0:-6]
    min10_creep_HS = creep_int[0:-6]
    tm_HS = pd.Series(tm_HS)
    New_Time=()
    New_Creep = ()
    Hourly_slip = np.array(Hourly_slip)
    HS_Cut = np.percentile(Hourly_slip,99)
    #print(HS_Cut)
    for j in range(len(Picked)):
        boolarr6 = (Picked.Time.loc[j].replace(tzinfo=None) - dt.timedelta(hours=120)<= tm_HS)\
        & (tm_HS <= Picked.Time.loc[j].replace(tzinfo=None)+dt.timedelta(hours=12))
        Creep_ST = tm_HS[boolarr6]
        HS_Creep = Hourly_slip[boolarr6]
        Creep_SS = min10_creep_HS[boolarr6]
        for p in range(len(HS_Creep)):
            if HS_Creep[p] >= HS_Cut:
                index_stop = p
                break
        Start_t = Creep_ST.iloc[p]
        NC = Creep_SS[p]
        New_Time = np.append(New_Time,Start_t)
        New_Creep = np.append(New_Creep,NC)
    Picked['T5'] = New_Time
    Picked['C5'] = New_Creep

    New_Time=()
    New_Creep = ()
    for j in range(len(Picked)):
        boolarr6 = (Picked.Time.loc[j].replace(tzinfo=None) - dt.timedelta(hours=96)<= tm_HS) \
        & (tm_HS <= Picked.Time.loc[j].replace(tzinfo=None)+dt.timedelta(hours=12))
        Creep_ST = tm_HS[boolarr6]
        HS_Creep = Hourly_slip[boolarr6]
        Creep_SS = min10_creep_HS[boolarr6]
        for p in range(len(HS_Creep)):
            if HS_Creep[p] >= HS_Cut:
                index_stop = p
                break
        Start_t = Creep_ST.iloc[p]
        NC = Creep_SS[p]
        New_Time = np.append(New_Time,Start_t)
        New_Creep = np.append(New_Creep,NC)
    Picked['T4'] = New_Time
    Picked['C4'] = New_Creep

    New_Time=()
    New_Creep = ()
    for j in range(len(Picked)):
        boolarr6 = (Picked.Time.loc[j].replace(tzinfo=None) - dt.timedelta(hours=72)<= tm_HS)\
        & (tm_HS <= Picked.Time.loc[j].replace(tzinfo=None)+dt.timedelta(hours=12))
        Creep_ST = tm_HS[boolarr6]
        HS_Creep = Hourly_slip[boolarr6]
        Creep_SS = min10_creep_HS[boolarr6]
        for p in range(len(HS_Creep)):
            if HS_Creep[p] >= HS_Cut:
                index_stop = p
                break
        Start_t = Creep_ST.iloc[p]
        NC = Creep_SS[p]
        New_Time = np.append(New_Time,Start_t)
        New_Creep = np.append(New_Creep,NC)
    Picked['T3'] = New_Time
    Picked['C3'] = New_Creep

    New_Time=()
    New_Creep = ()
    for j in range(len(Picked)):
        boolarr6 = (Picked.Time.loc[j].replace(tzinfo=None) - dt.timedelta(hours=48)<= tm_HS)\
        & (tm_HS <= Picked.Time.loc[j].replace(tzinfo=None)+dt.timedelta(hours=12))
        Creep_ST = tm_HS[boolarr6]
        HS_Creep = Hourly_slip[boolarr6]
        Creep_SS = min10_creep_HS[boolarr6]
        for p in range(len(HS_Creep)):
            if HS_Creep[p] >= HS_Cut:
                index_stop = p
                break
        Start_t = Creep_ST.iloc[p]
        NC = Creep_SS[p]
        New_Time = np.append(New_Time,Start_t)
        New_Creep = np.append(New_Creep,NC)
    Picked['T2'] = New_Time
    Picked['C2'] = New_Creep

    New_Time=()
    New_Creep = ()
    for j in range(len(Picked)):
        boolarr6 = (Picked.Time.loc[j].replace(tzinfo=None) - dt.timedelta(hours=24)<= tm_HS)\
        & (tm_HS <= Picked.Time.loc[j].replace(tzinfo=None)+dt.timedelta(hours=12))
        Creep_ST = tm_HS[boolarr6]
        HS_Creep = Hourly_slip[boolarr6]
        Creep_SS = min10_creep_HS[boolarr6]
        for p in range(len(HS_Creep)):
            if HS_Creep[p] >= HS_Cut:
                index_stop = p
                break
        Start_t = Creep_ST.iloc[p]
        NC = Creep_SS[p]
        New_Time = np.append(New_Time,Start_t)
        New_Creep = np.append(New_Creep,NC)
    Picked['T1'] = New_Time
    Picked['C1'] = New_Creep

    col = ['Start_Time','Start_Displacement','Warning']
    Creep_Events = pd.DataFrame(np.arange(3).reshape(1,3),columns =col)
    Creep_Events.drop([0],inplace=True)

    

    Warning2 = 0
    for i in range(len(Picked)):
        if ((Picked.T5.iloc[i]-Picked.T4.iloc[i])/dt.timedelta(minutes=1) == 0) & \
        ((Picked.T5.iloc[i]-Picked.T3.iloc[i])/dt.timedelta(minutes=1) == 0) & \
        ((Picked.T5.iloc[i]-Picked.T2.iloc[i])/dt.timedelta(minutes=1) == 0) & \
        ((Picked.T5.iloc[i]-Picked.T1.iloc[i])/dt.timedelta(minutes=1) == 0):
            Hourly_start = Picked.T5.iloc[i]
            Hourly_creep = Picked.C5.iloc[i]
            Warning = 0
            #new_row = {'Start_Time':Hourly_start,'Start_Displacement':Hourly_creep,'Warning':Warning}
            new_row = pd.DataFrame({'Start_Time':[Hourly_start],'Start_Displacement':[Hourly_creep],'Warning':[Warning]})
            Creep_Events = pd.concat((Creep_Events,new_row), ignore_index=True)
        else:
            Warning2 = Warning2+1
            Hourly_start5 = Picked.T5.iloc[i]
            Hourly_creep5 = Picked.C5.iloc[i]
            new_row = pd.DataFrame({'Start_Time':[Hourly_start5],'Start_Displacement':[Hourly_creep5],'Warning':[Warning2]})
            Creep_Events = pd.concat((Creep_Events,new_row), ignore_index=True)
            
            Hourly_start4 = Picked.T4.iloc[i]
            Hourly_creep4 = Picked.C4.iloc[i]
            new_row = pd.DataFrame({'Start_Time':[Hourly_start4],'Start_Displacement':[Hourly_creep4],'Warning':[Warning2]})
            Creep_Events = pd.concat((Creep_Events,new_row), ignore_index=True)
            
            Hourly_start3 = Picked.T3.iloc[i]
            Hourly_creep3 = Picked.C3.iloc[i]
            new_row = pd.DataFrame({'Start_Time':[Hourly_start3],'Start_Displacement':[Hourly_creep3],'Warning':[Warning2]})
            Creep_Events = pd.concat((Creep_Events,new_row), ignore_index=True)
            
            Hourly_start2 = Picked.T2.iloc[i]
            Hourly_creep2 = Picked.C2.iloc[i]
            new_row = pd.DataFrame({'Start_Time':[Hourly_start2],'Start_Displacement':[Hourly_creep2],'Warning':[Warning2]})
            Creep_Events = pd.concat((Creep_Events,new_row), ignore_index=True)
            
            Hourly_start1 = Picked.T1.iloc[i]
            Hourly_creep1 = Picked.C1.iloc[i]
            new_row = pd.DataFrame({'Start_Time':[Hourly_start1],'Start_Displacement':[Hourly_creep1],'Warning':[Warning2]})
            Creep_Events = pd.concat((Creep_Events,new_row), ignore_index=True)


    troughs,properties2 = scipy.signal.find_peaks(-creep_data, width = float(Troughs_width),distance = float(Troughs_distance)) # find troughs in the data that might align with creep start
    CD = creep_data[0:][troughs]
    CD_raw = creep_int[troughs]
    TM = tm_int[troughs]
    New_Time_T = []
    New_Creep_T = []
    for p in range(len(Creep_Events)): #for loop to find trough closest to point where the X_Corr picked the creep
        pivot  = Creep_Events.Start_Time.iloc[p]
        boolarr_trough = (Creep_Events.Start_Time.iloc[p]-dt.timedelta(hours=24) <=TM) & (TM <= Creep_Events.Start_Time.iloc[p]+dt.timedelta(hours=24))
        TM_trough = TM[boolarr_trough]
        #print(TM_trough,pivot)
        CD_raw_trough = CD_raw[boolarr_trough]
        tm_diff = pd.to_datetime(TM_trough)-pivot #earlier = negative, later = positive
        boolarrA = tm_diff == min(tm_diff, key=abs)
        TM2 = TM_trough[boolarrA]
        CD2 = CD_raw_trough[boolarrA]
        TM3 = TM2[0]
        New_Time_T.append(TM3)
        New_Creep_T.append(CD2)
    Creep_Events['Time_Trough'] = New_Time_T
    Creep_Events['Creep_Trough'] = New_Creep_T
    '''tm_HS = tm_int[0:-6]
    creep_HS = creep_int[0:-6]
    tm_HS = pd.Series(tm_HS)
    New_Time=()
    New_Creep = ()
    Hourly_slip = np.array(Hourly_slip)
    HS_Cut = np.percentile(Hourly_slip,99)
    #print(HS_Cut)
    for j in range(len(Picked_Creep)):
        boolarr6 = (Picked_Creep.Time.loc[j].replace(tzinfo=None) - dt.timedelta(hours=12)<= tm_HS) & (tm_HS <= Picked_Creep.Time.loc[j].replace(tzinfo=None)+dt.timedelta(hours=12))
        Creep_ST = tm_HS[boolarr6]
        HS_Creep = Hourly_slip[boolarr6]
        Creep_SS = creep_HS[boolarr6]
        for p in range(len(HS_Creep)):
            if HS_Creep[p] >= HS_Cut:
                index_stop = p
                break
        Start_t = Creep_ST.iloc[p]
        NC = Creep_SS[p]
        New_Time = np.append(New_Time,Start_t)
        New_Creep = np.append(New_Creep,NC)
    Picked_Creep['Start_Time'] = New_Time
    Picked_Creep['Start_offset'] = New_Creep
'''    

    End_Time = ()
    #print(len(TWT_DS),len(Daily_slip_WT))
    for j in range(len(Creep_Events)):
        boolarr5 = (Creep_Events.Time_Trough.loc[j].replace(tzinfo=None)<= TWT_DS)\
        & (TWT_DS <= Creep_Events.Time_Trough.loc[j].replace(tzinfo=None)+dt.timedelta(days=5))
        Creep_T = (TWT_DS)[boolarr5]
        Creep_DS = Daily_slip_WT[boolarr5]
        for p in range(len(Creep_DS)):
            if Creep_DS[p] < DS_Cut:
                index_stop = p
                break
        END_t = Creep_T.iloc[p]
        End_Time = np.append(End_Time,END_t)

    Creep_Events['End_Time'] = End_Time
    Creep_Events['Dur'] = Creep_Events.End_Time - Creep_Events.Time_Trough
 

    End_slip = ()
    for y in range(len(Creep_Events)):
        boolarr6 = (Creep_Events.Time_Trough.loc[y].replace(tzinfo=None)<= tm_int)\
            & (tm_int <= Creep_Events.End_Time.loc[y].replace(tzinfo=None))
        Creep_event_time = tm_int[boolarr6]
        Creep_event_slip = creep_int[boolarr6]   
        es = Creep_event_slip[-1]
        End_slip = np.append(End_slip,es)

    Creep_Events['End_Displacement'] = End_slip
    Creep_Events['Total_Slip'] = Creep_Events.End_Displacement - Creep_Events.Creep_Trough

    '''End_Time = ()
    for j in range(len(Picked)):
        boolarr5 = (Picked.Time.loc[j].replace(tzinfo=None)<= TWT_DS) \
            & (TWT_DS <= Picked.Time.loc[j].replace(tzinfo=None)+dt.timedelta(days=30))
        Creep_T = (TWT_DS)[boolarr5]
        Creep_DS = Daily_slip_WT[:-1][boolarr5]
        for p in range(len(Creep_DS)):
            if Creep_DS[p] < DS_Cut:
                index_stop = p
                break
        END_t = Creep_T.iloc[p]
        End_Time = np.append(End_Time,END_t)

    Picked['End_Time'] = End_Time
    Picked['Dur'] = Picked.End_Time - Picked.Start_Time

    Start_slip = ()
    End_slip = ()
    for y in range(len(Picked)):
        boolarr6 = (Picked.Time.loc[y].replace(tzinfo=None)<= tm_int)\
            & (tm_int <= Picked.End_Time.loc[y].replace(tzinfo=None))
        Creep_event_time = tm_int[boolarr6]
        Creep_event_slip = creep_int[boolarr6]   
        es = Creep_event_slip[-1]
        End_slip = np.append(End_slip,es)

    Picked['End_offset'] = End_slip
    Picked['Total_Slip'] = Picked.End_offset - Picked.Start_offset'''

    return Creep_Events



def x_corr_peaks(w_T_DS, X_Corr_peaks_width, Daily_slip):
    peaks,properties_1 = scipy.signal.find_peaks(w_T_DS,width = float(X_Corr_peaks_width)) #FIND LOCAL MAXIMA
    PEAK_WT = w_T_DS[peaks]
    PEAK_DS = Daily_slip[peaks]
    ticks = np.linspace(0,10,11)

    xedges2 = np.arange(-1,1.01,0.01)
    yedges2 = np.arange(-0.5,5.01,0.01)
    H2,xedges2,yedges2 = np.histogram2d(PEAK_WT, PEAK_DS, bins = (xedges2,yedges2), range= [[-1,1],[0,5]]) #CREATE HISTOGRAM OF W_T Vs DS
    H2 = H2.T
    ax1 = plt.figure()
    X2, Y2 = np.meshgrid(xedges2, yedges2) #CREATE GRID
    plt.pcolormesh(X2, Y2, H2, vmax=10, cmap = 'nipy_spectral_r',shading='flat',snap=True) #PLOT COLORMESH
    cbar = plt.colorbar(ticks=ticks)
    cbar.ax.tick_params(labelsize=20) 
    plt.tick_params(axis='both', labelsize=20)
    plt.xlabel('Cross-correlation coefficient peaks', fontsize = 24)
    plt.ylabel('Slip in 24hrs after cross-correlation peak (mm)', fontsize=24)
    plt.show()
    return


def X_corr_plot(w_T):
    bins_WT = np.arange(-1,1,0.01)
    plt.figure()
    #sns.distplot(w_T, bins=bins_WT, hist=True,color="b")
    plt.hist(w_T,bins=bins_WT) #create histogram to get upper x-corr band for creep
    plt.xlabel('X-corr coefficient')
    plt.ylabel('Frequency')
    plt.show()
    return

def X_corr(creep, template, time):
    u = template
    u = u - np.mean(u)#remove straight line aspect
    #print(time)
    boolarr2 = (dt.datetime(1975,1,1,0,0,0) <= pd.to_datetime(time)) & (pd.to_datetime(time) <= dt.datetime(2021,1,1,0,0,0))
    v = creep[boolarr2]
    t_w_T = time[boolarr2]

    w_T = []

    for i in range(len(v)-len(u)):
        b = 0
        d = 0
        f = 0
        v_window = v[i:i+len(u)] #extract V-window data
        v_window = v_window - np.mean(v_window) #remove straight line aspect
        for k in range(len(u)):
            a = u[k]*v_window[k] # Caluculate numerator
            b = b+a #sum numerator
            c = (u[k]**2) #Calculate denominator
            d = c+d #Sum part of denominator
            e = (v_window[k]**2) #Calculate denominator
            f = f + e #Sum part of denominator
            w = b/np.sqrt(d*f) #calculate cross-correlation value
        w_T = np.append(w_T,w) #append to array
    
    x_corr = pd.DataFrame({'x_corr':w_T,'TWT':t_w_T[0:-len(u)],'V':v[0:-len(u)]})
    isExist = os.path.exists('../../../Creeping_section_CA/X_corr')
    if not isExist:
        os.mkdir('../../../Creeping_section_CA/X_corr')
    x_corr.to_csv('../../../Creeping_section_CA/X_corr/x_corr_test_xhr.csv')
    return x_corr

def template_finder(time,creep):
    fig=plt.figure()
    ax = plt.subplot(1,1,1)#, xlim=(0,1), ylim=(0,1), autoscale_on=False)
    ax.plot(time, creep, 'red')
    scale = 1.1
    zp = ZoomPan()
    figZoom = zp.zoom_factory(ax, base_scale = scale)
    figPan = zp.pan_factory(ax)
    s = 1
    plt.show()
    pts = plt.ginput(2,timeout = -1)
    plt.close('all')
    #print(pts)

    Coords_creep=[]
    Creep_identified=[]
    for sublist in pts:
        for item in sublist:
            Coords_creep.append(item)
    Creep_identified = [Coords_creep]
    #print(Creep_identified)




    df2=pd.DataFrame(Creep_identified,columns=['Start_Time','Start_offset','End_Time', 'End_offset'])
    df2.drop('Start_offset', axis='columns', inplace=True)
    df2.drop('End_offset', axis='columns', inplace=True)
            
    #Convert to datetime array
    df2.Start_Time = mdates.num2date(df2.Start_Time)
    df2.End_Time = mdates.num2date(df2.End_Time)
            
    #Round to nearest 1 mins
    s1 = df2.iloc[:,0]
    s2 = df2.iloc[:,1]

    s3 = pd.Series(s1).dt.round("10min")
    s4 = pd.Series(s2).dt.round("10min")
    df2.Start_Time = s3
    df2.End_Time = s4
    return df2


def import_text(path):
    ''' import text file for creepmeter data
    input         path: path to data
    return          tm: time for data
    return min10_creep: slip for data'''

    vls = np.loadtxt(path, dtype = str)
    Year  = vls[:,0].astype(int)
    Time  = vls[:,1].astype(float)
    creep  = vls[:,2].astype(float)
    tm =np.array([dt.datetime(Year[k],1,1) + dt.timedelta(days = Time[k] -1) for k in range (0, len(Year))])
    return tm, creep

def import_csv(path):
    ''' import csv file for creepmeter data
    input         path: path to data
    return          tm: time for data
    return min10_creep: slip for data'''
    csv_imported = pd.read_csv(path,names=['Time','Slip'])
    creep = csv_imported['Slip']
    tm = csv_imported['Time']
    return tm, creep


def interpolate(tm,creep,sample_rate,sample_rate_beg):
    '''interpolate the time series data 
        input          tm: time
        input       creep: slip
        input sample_rate: time difference between samples in minutes
        return     tm_int: interpolated time
        return  creep_int: interpolated slip'''
    
    Time = pd.Series(pd.to_datetime(tm)) #convert to pandas series
    creeping = pd.DataFrame({'Time':Time, 'Tm': Time,'Creep':creep}) #create a pandas dataframe
    creeping.Time = creeping.Time.dt.round("{k}min".format(k=sample_rate)) #round creep times to nearest 10 mins (make evenly spaced)
    creeping.Tm = creeping.Tm.dt.round("{k}min".format(k=sample_rate))
    creeping.set_index('Time',inplace=True) #set index of the dataframe
    creeping.drop_duplicates(subset=['Tm'], inplace=True) 
    upsampled = creeping.resample('{k}min'.format(k=sample_rate)).ffill(1) #upsample the timeframe to get a uniformly spaced dataset
    upsampled['Time'] = upsampled.index #get time as a column
    interpolated = upsampled.interpolate(method='ffill') #interpolate the dataset to get a continious record evenly spaced at 10 mins
    tm_int = np.array(interpolated.Time) #make Time and creep into Numpy array.
    creep_int = np.array(interpolated.Creep)
    return tm_int, creep_int, upsampled


def slip_difference(sampling, data, duration):
    """Calculates the hourly slip based on the sampling rate of the creepmeter
    Input: sampling = the sampling rate of the instrument (e.g., 1 for 1 min, 10 for 10 mins, 0.5 for 30 s)
    Input: data = list of [time,slip] for the creepmeter
    Input: duration = time over which you want the difference calculated (e.g., day, hour)
    Return: hr_slip = hourly slip, mm
    
    """
    slip = ()
    if duration == 'day':
        sam_freq = int(1440/sampling)+1
    elif duration == 'hour':
        sam_freq = int(60/sampling)
    
    slip = data[1][:-sam_freq] - data[1][sam_freq:]
    return slip

### Scrolling for zoom on interactive plot from: https://stackoverflow.com/users/1629298/seadoodude

class ZoomPan:
    def __init__(self):
        self.press = None
        self.cur_xlim = None
        self.cur_ylim = None
        self.x0 = None
        self.y0 = None
        self.x1 = None
        self.y1 = None
        self.xpress = None
        self.ypress = None


    def zoom_factory(self, ax, base_scale = 2.):
        def zoom(event):
            cur_xlim = ax.get_xlim()
            cur_ylim = ax.get_ylim()

            xdata = event.xdata # get event x location
            ydata = event.ydata # get event y location

            if event.button == 'down':
                # deal with zoom in
                scale_factor = 1 / base_scale
            elif event.button == 'up':
                # deal with zoom out
                scale_factor = base_scale
            else:
                # deal with something that should never happen
                scale_factor = 1
                print(event.button)

            new_width = (cur_xlim[1] - cur_xlim[0]) * scale_factor
            new_height = (cur_ylim[1] - cur_ylim[0]) * scale_factor

            relx = (cur_xlim[1] - xdata)/(cur_xlim[1] - cur_xlim[0])
            rely = (cur_ylim[1] - ydata)/(cur_ylim[1] - cur_ylim[0])

            ax.set_xlim([xdata - new_width * (1-relx), xdata + new_width * (relx)])
            ax.set_ylim([ydata - new_height * (1-rely), ydata + new_height * (rely)])
            ax.figure.canvas.draw()

        fig = ax.get_figure() # get the figure of interest
        fig.canvas.mpl_connect('scroll_event', zoom)

        return zoom

    def pan_factory(self, ax):
        def onPress(event):
            if event.inaxes != ax: return
            self.cur_xlim = ax.get_xlim()
            self.cur_ylim = ax.get_ylim()
            self.press = self.x0, self.y0, event.xdata, event.ydata
            self.x0, self.y0, self.xpress, self.ypress = self.press

        def onRelease(event):
            self.press = None
            ax.figure.canvas.draw()

        def onMotion(event):
            if self.press is None: return
            if event.inaxes != ax: return
            dx = event.xdata - self.xpress
            dy = event.ydata - self.ypress
            self.cur_xlim -= dx
            self.cur_ylim -= dy
            ax.set_xlim(self.cur_xlim)
            ax.set_ylim(self.cur_ylim)

            ax.figure.canvas.draw()

        fig = ax.get_figure() # get the figure of interest

        # attach the call back
        fig.canvas.mpl_connect('button_press_event',onPress)
        fig.canvas.mpl_connect('button_release_event',onRelease)
        fig.canvas.mpl_connect('motion_notify_event',onMotion)

        #return the function
        return onMotion
