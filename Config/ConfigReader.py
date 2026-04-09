import json

def read_config(config_path: str) -> dict:
    with open(config_path, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
        #print(config_data)
    return config_data
