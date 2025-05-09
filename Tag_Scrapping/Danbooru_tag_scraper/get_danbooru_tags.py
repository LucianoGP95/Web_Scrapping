import csv, time, os
import requests
# Based off: https://gist.github.com/bem13/596ec5f341aaaefbabcbf1468d7852d5

# Open a file to write
def get_tags_raw(url, output_file, category_selection: str, postcount_filter: str ="100", rewrite_existent: bool =True):
    output_file_path = output_file
    category_dict = {
        "General": [0],
        "Artist": [1],
        "Copyright": [3],
        "Character": [4],
        "Meta": [5],
        "Author": [0],  # Optional alias
        "All": [0, 1, 3, 4, 5]
    }
    try:
        category_filter = category_dict.get(category_selection)
    except Exception as e:
        print(e)
    if rewrite_existent == False and os.path.exists(output_file_path):
        message = f"An output file already exists!: {output_file} \n Skipping get_tags_raw()"
        print(message)
        return
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header
        writer.writerow(['name', 'post_count', "category"])
        # Loop through pages 1 to 1000
        for page in range(1, 1001):
            # Update the URL with the current page
            url = f'{url}&page={page}'
            # Fetch the JSON data
            response = requests.get(url)
            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()
                # Break the loop if the data is empty (no more tags to fetch)
                if not data:
                    print(f'No more data found at page {page}. Stopping.', flush=True)
                    break
                # Write the data
                for item in data:
                    if item['post_count'] < int(postcount_filter):
                        print(f"Reached minimum post count: {postcount_filter}\nStopping get_tags_postcount()")
                        return
                    if item['category'] in category_filter:
                        writer.writerow([item['name'], item['post_count'], item['category']])
                # Explicitly flush the data to the file
                file.flush()
            else:
                print(f'Failed to fetch data for page {page}. HTTP Status Code: {response.status_code}', flush=True)
                break
            print(f'Page {page} processed.', flush=True)
            # Sleep for 1 second so we don't DDOS Danbooru too much
            time.sleep(1)
    print(f'Data has been written to {output_file}', flush=True)

def get_tags_refined(base_file, output_file, rewrite_existent=False):
    base_file_path = base_file
    output_file_path = output_file

    if not rewrite_existent and os.path.exists(output_file_path):
        print(f"An output file already exists!: {output_file} \nSkipping get_tags_refined()")
        return
    # Read the og file and write the new one altogether
    with open(base_file_path, mode='r', newline='', encoding='utf-8') as infile, \
        open(output_file_path, mode='w', newline='', encoding='utf-8') as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        header = next(reader)
        name_index = header.index("name")

        # Read all names into a list
        tag_names = [row[name_index] for row in reader]

        # Sort the tag names
        tag_names.sort()

        # Write header and sorted tags
        for name in tag_names:
            writer.writerow([name])

    print(f'Data has been refined and written to {output_file}')

if __name__ == "__main__":
    pass