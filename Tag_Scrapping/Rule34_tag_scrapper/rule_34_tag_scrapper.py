import requests
import xml.etree.ElementTree as ET
import time

BASE_URL = 'https://api.rule34.xxx/index.php?page=dapi&s=tag&q=index'
MIN_COUNT = 1

def keep_first_term_only(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    updated_lines = []
    for line in lines:
        first_term = line.strip().split()[0]
        updated_lines.append(first_term + '\n')

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)

def get_artist_tags(min_count=1, output_file=None):
    page = 0
    total_collected = 0
    all_artists = []

    if output_file:
        # Limpiamos el archivo al inicio
        open(output_file, 'w', encoding='utf-8').close()

    try:
        while True:
            params = {
                'limit': 1000, # Max allowed by Rule34
                'pid': page,
            }
            print(f"Fetching page {page}...")
            response = requests.get(BASE_URL, params=params)

            if response.status_code != 200 or not response.text.strip():
                print("Failed to get data or empty response")
                break

            try:
                root = ET.fromstring(response.text)
            except ET.ParseError as e:
                print(f"XML parse error: {e}")
                break

            tags = root.findall('tag')
            if not tags:
                print("No more tags, stopping.")
                break

            qualifying_tags = []
            for tag in tags:
                tag_type = tag.attrib.get('type')
                count = int(tag.attrib.get('count', 0))
                name = tag.attrib.get('name')
                # type '1' is artist, and count filter applied
                if tag_type == '1' and count >= min_count:
                    qualifying_tags.append((name, count))

            if qualifying_tags:
                total_collected += len(qualifying_tags)
                all_artists.extend(qualifying_tags)

                if output_file:
                    with open(output_file, 'a', encoding='utf-8') as f:
                        for name, count in qualifying_tags:
                            print(f"Collected artist tag: {name} (count: {count})")
                            f.write(f"{name} ({count})\n")
            else:
                print(f"No qualifying artist tags on page {page}, continuing...")

            page += 1
            time.sleep(1)  # evita sobrecarga

    except KeyboardInterrupt:
        print("\nInterrupted by user.")

    print(f"Total artist tags collected: {total_collected}")
    return all_artists


# Ejecutar y guardar en archivo:
artists = get_artist_tags(min_count=MIN_COUNT, output_file='rule34_artist_tags.csv')
keep_first_term_only('./rule34_artist_tags.csv')

# Imprimir resumen:
print(f"\nFound {len(artists)} artist tags with >= {MIN_COUNT} posts:")
for name, count in artists:
    print(f"{name} ({count})")
