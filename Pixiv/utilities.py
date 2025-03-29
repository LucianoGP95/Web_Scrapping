def get_config(config_file):
    config = {}
    with open(config_file) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = map(str.strip, line.split("=", 1))
                config[key] = value
    return config  # Return the dictionary instead of modifying globals()

if __name__ == "__main__":
    config_file = "config.txt"
    config = get_config(config_file)
    print(config.get("directory_path"))  # Now it should print the value from the config file