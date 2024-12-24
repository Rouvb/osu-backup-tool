import asyncio
import json
import os
import re
import sys

import requests


class JsonManager():
    async def write(self, json_data):
        with open("map_list.json", "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)

    async def read(self):
        with open("map_list.json", "r", encoding="utf-8") as f:
            json_data = json.load(f)
            return json_data

async def download_beatmap():
    json_manager = JsonManager()
    map_list = await json_manager.read()
    download_count = 0

    for beatmap in map_list:
        download_count += 1
        url = f"https://api.nerinyan.moe/d/{beatmap}"
        file_path = f"beatmaps/{beatmap}.osz"

        if os.path.exists(file_path):
            print(f"Skipping Download... ({download_count}/{len(map_list)})")
            continue

        try:
            print(f"Downloading {beatmap}... ({download_count}/{len(map_list)})")
            # Update progress bar
            percent_complete = (download_count / len(map_list)) * 100
            bar_length = 30  # Length of progress bar
            block = int(bar_length * percent_complete // 100)
            progress_bar = '█' * block + '-' * (bar_length - block)

            sys.stdout.write(f"\r|{progress_bar}| {percent_complete:.2f}%\n")
            sys.stdout.flush()

            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(file_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=4096):
                    f.write(chunk)

        except Exception as e:
            print(e)


async def get_beatmap_list(osu_path):
    if not os.path.exists(osu_path):
        print("osu! folder doesn't exist\n")
        return

    osu_songs_dir = osu_path + "/songs"
    dir_names = [name for name in os.listdir(osu_songs_dir) if os.path.isdir(os.path.join(osu_songs_dir, name))]
    beatmap_list = []
    for dir_name in dir_names:
        match = re.match(r'(\d+)', dir_name)
        if match:
            beatmap_list.append(match.group(1))

    print(f"\n{len(beatmap_list)} beatmap files has been stored to json from your osu! folder\n")
    return beatmap_list

async def main():
    select_type = int(input("0 - Get List of Beatmaps\n1 - Download Beatmaps from List\n2 - Exit the program\n\nInput your choice: "))
    json_manager = JsonManager()

    if select_type == 0:
        osu_path = input("Enter your osu! path: ")
        beatmap_list = await get_beatmap_list(osu_path)
        await json_manager.write(beatmap_list)
        await main()

    if select_type == 1:
        await download_beatmap()
        print("Beatmap Download Complete\n")
        await main()

    if select_type == 2:
        return

asyncio.run(main())