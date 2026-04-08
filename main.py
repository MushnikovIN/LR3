from Config.ConfigReader import read_config


circuit_data = read_config('Config/config.json')

#circuit1  = Curcuit(circuit_data)

circuit_data1 = circuit_data.get('circuit', {})
branches_data = circuit_data1.get('branches', [])
print(circuit_data1)
print(branches_data)