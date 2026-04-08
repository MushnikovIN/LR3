from Config.ConfigReader import read_config


circuit_data = read_config('Config/config.json')

circuit1  = Curcuit(circuit_data)