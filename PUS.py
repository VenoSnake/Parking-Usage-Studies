import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from bisect import bisect_left
from shapely.geometry import Polygon
import time

def BinarySearch(a, x):
    i = bisect_left(a, x)
    if i != len(a) and a[i] == x:
        return i
    else:
        return -1

def vehicle_times(veh_times):
    value_max = max(veh_times.values())
    count = 0
    while value_max > 0:
        count = count + 1
        value_max = value_max // 10
    print '      Car   :    Times'
    for keys, values in veh_times.items():
        print '|', ' ', keys, ' :', '    ', values, '  ' * count, '|'

def PolygonArea(corners):
    n = len(corners) # of corners
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += corners[i][0] * corners[j][1]
        area -= corners[j][0] * corners[i][1]
    area = abs(area) / 2.0
    print area

# -----------------------------------------------------------------------------------------------------------------------------------
# 1.Load And PreProcess The Data (park_data):   [Generalized]

park_data = pd.read_excel(r'/Users/nikhil/Desktop/Project/PUS/Utilities/Parking_Usage_Survey.xlsx')
park_data = np.array(park_data)
park_data = np.sort(park_data, axis=0)
print '-----------------------------------------------------------------------------------------------------------------'
period = float(input('Enter The Period Interval (hrs) :  '))
start_tim_ = float(input('Enter The Starting Time (H.MM) (Ex : 0.5 = 30 Min) : '))
lots = float(input('Number Of Lots : '))
print '-----------------------------------------------------------------------------------------------------------------'
end_time = start_tim_ + ((period * park_data.shape[1]) - period)
for i in range(park_data.shape[0]):
    for j in range(park_data.shape[1]):
        if np.isnan(park_data[i][j]):
            park_data[i][j] = 0
# -----------------------------------------------------------------------------------------------------------------------------------
# 2.Obtaining Different Vehicles Present (veh_list):    [Generalized]

start_time = time.time()
veh = np.reshape(park_data, (1, -1))[0]   # All The Vehicle's (A Single Vehicle Can Be More Than Once)
veh_list = []
[veh_list.append(veh) for veh in veh if veh not in veh_list]    # Appends Different Vehicle's Which Had Come Into The Parking Lot
# -----------------------------------------------------------------------------------------------------------------------------------
# 3.Obtaining In How Many Different Period's Of Time A Single Particular Vehicle Is Present (veh_times): [Generalized]

veh_times = {}
for vehicle in veh_list:  # Searching For This Particular Vehicle In Various Time-Slots
    seen_times = 0
    for i in range(park_data.shape[1]):
        veh_slot =[]
        [veh_slot.append(val) for val in park_data[:, i] if val != 0]
        if BinarySearch(veh_slot, vehicle) != -1:
            seen_times += 1
    veh_times[str(vehicle)] = seen_times
del veh_times['0.0']
#vehicle_times(veh_times)
# -----------------------------------------------------------------------------------------------------------------------------------
# 4. Obtaining The Parking Load (DataFrame:df): [Generalized]

print '                     Parking Load'
print
veh_count = []
val_car = veh_times.values()
val_max = max(val_car)
times = [x for x in range(1, val_max + 1, 1)]
dur = [x * period for x in range(1, len(times) + 1)]
for val_times in times:
    count = 0
    for val_ in val_car:
        if val_times == val_:
            count += 1
    veh_count.append(count)
park_load = [float(a)*b for a,b in zip(veh_count, dur)]
df = {'Times Seen' : times, 'Duration (Hrs)' : dur, 'No. Of Vehicles' : veh_count, 'Parking Load' : park_load}
df = pd.DataFrame(df)
cols = df.columns.tolist()
cols = cols[-1:] + cols[:-1]
df = df[cols]
print df
print '                                                       ---------'
print '                                                         ', sum(df.iloc[:, 3])
print '                                                       ---------'
# -----------------------------------------------------------------------------------------------------------------------------------
print '-----------------------------------------------------------------------------------------------------------------'
# 5. Parking Accumulation & Parking Index (park_stud):  [Generalized]

print '             Parking Accumulation & Parking Index'
print
park_accum = []
park_index = []
time_ = [start_tim_]
park_stud = {}
for i in range(park_data.shape[1] - 1):
    time_.append(time_[i] + period)
for i in range(park_data.shape[1]):
    count = 0
    for j in range(len(park_data[:,i])):
        if park_data[:,i][j] != 0:
            count += 1
    park_accum.append(count)
max_accum = max(park_accum)
for val in park_accum:
    park_index.append(float(val) / float(max_accum) * 100)
park_stud = {'Time': time_,
                   'Parking Accumulation' : park_accum,
                   'Parking Index (%)' : park_index}
park_stud = pd.DataFrame(park_stud)
cols = park_stud.columns.tolist()
cols = cols[-1:] + cols[:-1]
park_stud = park_stud[cols]
print park_stud
print '-----------------------------------------------------------------------------------------------------------------'
# -----------------------------------------------------------------------------------------------------------------------------------
# 5.Printing Results:   [Generalized]

print '                   ***RESULTS***'
print
print 'Parking Load = ', sum(df.iloc[:, 3])
print 'Parking Turnover = ', sum(df.iloc[:, 3]) / lots, 'Veh/Lot'
print
print '-----------------------------------------------------------------------------------------------------------------'
print 'Time Taken = ', time.time() - start_time
# -----------------------------------------------------------------------------------------------------------------------------------

# 6.Plotting Parking Accumulation Vs Duration: [Generalized]

duration = [period]
for i in range(park_data.shape[1] - 1):
    duration.append(duration[i] + period)
plt.scatter(duration, park_accum)
plt.plot(duration, park_accum)
plt.fill_between(duration, park_accum, color='skyblue', alpha=0.50)
plt.xlabel('Duration (Hrs)', size=15)
plt.ylabel('Parking Accumulation', size=15)
# -----------------------------------------------------------------------------------------------------------------------------------
# 7. Verification With Area Under Curve
print '-----------------------------------------------------------------------------------------------------------------'
print '             Verification By Area Under Curve (Approximate)'
poly_coor = []
for i in range(len(duration)):
    poly_coor.append((duration[i], park_accum[i]))
poly_coor.insert(0, (duration[0], 0))
poly_coor.insert(len(poly_coor), (duration[len(duration) - 1], 0))
polygon = Polygon(poly_coor)
area = polygon.area
error = sum(df.iloc[:, 3]) - area
print 'Area Under Curve     = ', area
print 'Approximate Error (%) = ', (abs(error) / area) * 100
print '-----------------------------------------------------------------------------------------------------------------'
print '                 END OF ANALYSIS'
print '-----------------------------------------------------------------------------------------------------------------'
plt.show()