import re

def get_config(config_file):
    config = {}
    with open(config_file, encoding='utf-8') as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                key, value = map(str.strip, line.split("=", 1))
                key = sanitize_filename(key)
                config[key] = value
    return config  # Return the dictionary instead of modifying globals()

def sanitize_filename(filename):
    """Remove non-valid windows characters."""
    return re.sub(r'[<>:"/\\|?*]', '', filename)

if __name__ == "__main__":
    config_file = ".\\config\\config.txt"
    config = get_config(config_file)
    print(f"Config file: {config}")
    author_file = ".\\config\\authors.txt"
    author_urls = get_config(author_file)
    print(f"Authors file: {author_urls}")