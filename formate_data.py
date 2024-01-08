from sklearn.linear_model import LinearRegression
import numpy as np
import netCDF4
from matplotlib import pyplot as plt
from joblib import Parallel, delayed
import multiprocessing

all_data = np.array([netCDF4.Dataset(f"formatted_monthly/{i}.nc")["GWRPM25"] for i in range(300)])
lat = netCDF4.Dataset(f"formatted_monthly/{0}.nc")["lat"]
lon = netCDF4.Dataset(f"formatted_monthly/{0}.nc")["lon"]
error = np.zeros(300)
cnt = 0

def train_and_compute_error(month, i, j):
    if np.isnan(all_data[month, i, j]):
        return
    global cnt
    cnt += 1
    current_data = (np.array(list(enumerate(all_data[month::12, i, j]))))
    training_data_length = int(len(current_data) * 0.5)
    np.random.shuffle(current_data)
    X = [[a] for a in (current_data[:training_data_length, 0])]
    y = [[a] for a in (current_data[:training_data_length, 1])]
    reg = LinearRegression().fit(X, y)
    predictions = reg.predict([[data_point] for data_point in np.arange(len(current_data))]).flatten()
    # print(len(predictions))
    global error
    # error += ((predictions - current_data[:, 1]) ** 2)
    for i, e in enumerate(((predictions - current_data[:, 1]) ** 2)):
        error[12 * i + month] += e

print("Start", multiprocessing.cpu_count())
Parallel(n_jobs=multiprocessing.cpu_count(), require='sharedmem')(delayed(train_and_compute_error)(month, i, j) for i in range(len(lat)) for j in range(len(lon)) for month in range(12))
error /= cnt/12
error = np.sqrt(error)
print_error(error)

def something(): 
    for i, _lat in enumerate(lat):
        for j, _lon in enumerate(lon):
            for month in range(12):
                if not np.isnan(all_data[month, i, j]):
                    train_and_compute_error(month, i, j)
                    return
                    current_data = (np.array(list(enumerate(all_data[month::12, i, j]))))
                    np.random.shuffle(current_data)
                    training_data_length = int(len(current_data) * 0.2)
                    y = [[a] for a in (current_data[:training_data_length, 1])]
                    X = [[a] for a in (current_data[:training_data_length, 0])]
                    reg = LinearRegression().fit(X, y)
    
                    # print(reg.predict([[data_point] for data_point in np.arange(len(all_data))]).flatten())
                    plt.figure()
                    plt.plot(all_data[month::12, i, j])
                    plt.plot(reg.predict([[data_point] for data_point in np.arange(len(current_data))]).flatten())
                    plt.show()
                    return
                    
# something()