import subprocess

subprocess.run("colcon build --packages-select sensor_interfaces sensor_thermometer sensor_barometer sensor_oxygen sensor_salinity",shell=True)