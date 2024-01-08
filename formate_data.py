import numpy as np
import netCDF4
import reverse_geocode

initial_year = 1998
initial_month = str(1).zfill(2)
fp=f'monthly/V5GL04.HybridPM25c_0p10.Asia.{initial_year}{initial_month}-{initial_year}{initial_month}.nc'
nc = netCDF4.Dataset(fp)

lat = np.round(nc.variables["lat"], 2)
lon = np.round(nc.variables["lon"], 2)

lat_mask = (lat > 8.06666667) & (lat < 37.1) # latitude of india
lon_mask = (lon > 68.1166667) & (lon < 97.4166667) # longitude of india

lat = lat[lat_mask]
lon = lon[lon_mask]

nc.close()

def read_and_format_data(file_idx):
    year = 1998 + int(file_idx/12)
    month = str(file_idx % 12 + 1).zfill(2)
    fp=f'monthly/V5GL04.HybridPM25c_0p10.Asia.{year}{month}-{year}{month}.nc'
    nc = netCDF4.Dataset(fp)
    data = nc.variables["GWRPM25"][lat_mask, lon_mask]

    for i, _lat in enumerate(lat):
        for j, _lon in enumerate(lon):
            coords = (_lat, _lon),
            obj = reverse_geocode.search(coords)
            if obj[0]['country'] != 'India':
                data[i][j] = np.nan

    nc.close()
    return data

for i in range(0, 300):
    print(f'Writing file {i} of 300')
    
    ncfile = netCDF4.Dataset(f'formatted_monthly/{i}.nc', mode='w', format='NETCDF4_CLASSIC')
    
    lat_dim = ncfile.createDimension('lat', len(lat))     # latitude axis
    lon_dim = ncfile.createDimension('lon', len(lon))    # longitude axis
    
    lat_var = ncfile.createVariable('lat', np.float64, ('lat',))
    lat_var.units = 'degrees_north'
    lat_var.long_name = 'latitude'
    
    lon_var = ncfile.createVariable('lon', np.float64, ('lon',))
    lon_var.units = 'degrees_east'
    lon_var.long_name = 'longitude'
    
    GWRPM25 = ncfile.createVariable('GWRPM25', np.float32, ('lat','lon')) 
    
    lat_var[:] = lat
    lon_var[:] = lon
    GWRPM25[:,:] = read_and_format_data(i)
    
    ncfile.close()

print("Done!")