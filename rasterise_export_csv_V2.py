import subprocess
import json
import os
import arcpy
from arcpy import env
from arcpy.sa import *
import pandas as pd 


os.chdir('E:/WorldPOP_global/raster_extr_csv')
gdb_list = ['fGDB_UN_USBC_Nat_agesex_2000_20.gdb', 'fGDB_EUROSTAT_agesex_2000_20.gdb', 'fGDB_USCB_SubNat_agesex_2000_20.gdb']
gdb_list = ['fGDB_EUROSTAT_agesex_2000_20.gdb', 'fGDB_USCB_SubNat_agesex_2000_20.gdb']
csv_path='E:/WorldPOP_global/raster_extr_csv/'


def download_FTP(iso, path):
	if iso == "ANR":
		iso = "AND"
	ftp = FTP("***********")
	ftp.login('*****', '**********')
	ftp.cwd('WP515640_Global')
	ftp.cwd('Covariates')
	ftp.cwd(iso)
	ftp.cwd('Mastergrid')
	ftp.retrlines("LIST")
	listing = []
	ftp.retrlines("LIST", listing.append)
	words = listing[0].split(None, 8)
	filename = words[-1].lstrip()
	local_filename = os.path.join(path, filename)
	lf = open(local_filename, "wb")
	ftp.retrbinary("RETR " + filename, lf.write)
	lf.close()
	return filename

for gdb in gdb_list:
	env.workspace = env.scratchWorkspace = gdb

	list_data = arcpy.ListDatasets()

	for dataset in list_data:
		env.workspace = env.scratchWorkspace = gdb + "/" + dataset
		list_features = arcpy.ListFeatureClasses()
		folder_path = csv_path + dataset
		os.mkdir(folder_path)
		raster = os.path.join(folder_path, download_FTP(dataset, folder_path))
		env.cellSize = raster
		env.snapRaster = raster
		env.extent = raster
		for index, i in enumerate(list_features):
			if index == 0:
				out_raster_dataset = folder_path + "/" + i[:4] + "_Rasterised_Stage.tif"
				arcpy.PolygonToRaster_conversion(i, "OBJECTID", out_raster_dataset)
				del out_raster_dataset
			out_path = csv_path + dataset 
			name = i + ".csv"
			arcpy.TableToTable_conversion(i,out_path, name)
			df = pd.read_csv(out_path + "/" + name)
			#df = df.drop(['OID', 'Shape_Length', 'Shape_Area'], axis=1)
			df = df.drop(['OID'], axis=1)
			df = pd.DataFrame(df)
			df.insert(0, 'FID', value= df.index + 1)
			df.to_csv(out_path + "/" + name, index=False)		
			del name, df, out_path
		print dataset + "Done"
		del env.workspace, env.scratchWorkspace, list_features, folder_path, raster, env.cellSize, env.snapRaster, env.extent

folders = ['ANR', 'LCA', 'IDN', 'CHE', 'SXM', 'HTI', 'ZAF', 'ESH', 'KEN', 'FJI', 'BMU', 'KOS', 'TUV', 'IMN', 'ZWE', 'LSO', 'ETH', 'ZMB', 'GUM', 'HUN', 'PRT', 'WLF', 'VGB', 'PLW', 'LVA', 'IRL', 'MKD', 'BRN', 'AUT', 'MHL', 'BHR', 'SPR', 'ABW', 'ISL', 'TUR', 'SYR', 'SWE', 'TZA', 'MOZ', 'BEL', 'FSM', 'GIB', 'NRU', 'FIN', 'BLM', 'MDV', 'MWI', 'POL', 'MLT', 'DOM', 'NCL', 'NLD', 'GUY', 'DJI', 'ITA', 'LTU', 'MNP', 'CYP', 'SVK', 'NOR']


def fix_rasters(folder):
	new_path = os.path.join(path, folder)
	os.chdir(new_path)
	L0 = folder.lower() + "_grid_100m_ccidadminl0.tif"
	wrong_raster = folder + "__Rasterised_Stage.tif"
	right_raster = folder + "_Rasterised_Stage_clip.tif"
	#L0 = folder + "/" + folder.lower() + "_grid_100m_ccidadminl0.tif"
	#wrong_raster = folder + "/" + folder + "_Rasterised_Stage.tif"
	#right_raster = folder + "/" + folder + "_Rasterised_Stage_clip.tif"
	info = subprocess.check_output(['gdalinfo {0} -json'.format(L0)], shell=True)
	str_info = info.decode('utf-8').replace("'", '"')
	json_info = json.loads(str_info)
	upper_left = json_info['cornerCoordinates']['upperLeft']
	lower_right = json_info['cornerCoordinates']['lowerRight']
	subprocess.call(['gdal_translate -projwin {0} {1} {2} {3} -of GTiff {4} {5}'.format(upper_left[0], upper_left[1], lower_right[0], lower_right[1], wrong_raster, right_raster)], shell=True)
	print folder + " done"
	del new_path, L0, wrong_raster, right_raster, info, str_info, json_info, upper_left, lower_right


for folder in folders:
	fix_rasters(folder)