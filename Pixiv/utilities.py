def get_config(config_file):
    config = {}
    with open(config_file) as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = map(str.strip, line.split("=", 1))
                config[key] = value
    return config  # Return the dictionary instead of modifying globals()

def get_authors(author_file):
    author_urls = get_config(author_file)
    urls = []
    [urls.append(author_url) for author_url in author_urls.values()]
    return urls

if __name__ == "__main__":
    config_file = "config.txt"
    config = get_config(config_file)
    author_file = "authors.txt"
    print(get_authors(author_file))
    print(config.get("directory_path"))  # Now it should print the value from the config file