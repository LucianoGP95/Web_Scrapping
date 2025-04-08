

url = "https://www.youtube.com/watch?v=ulfeM8JGq7s&list=RDAY38LoQhl4E&index=5&ab_channel=Vivziepop"
prefix = url.split('=')[0]
print(prefix)
id = url.split('=')[1].split("&")[0]
print(id)
new_url = prefix + id
print(new_url)