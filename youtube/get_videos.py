import os
import json
import re

import googleapiclient.discovery


def main():
    description_regex = re.compile(r'Original filename: "(.+)"')
    title_regex = re.compile(r'Tibia \[(\d\.\d{1,2})\] (.*)')

    api_service_name = 'youtube'
    api_version = 'v3'
    api_key = None
    with open('.apikey', 'r') as f:
        api_key = f.readline().strip()

    youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)

    videos = dict()

    i = 0
    next_page_token = None
    while True:
        request = youtube.search().list(
            part='snippet',
            channelId='UCLvAMwZjm9aUUeJ-wVDMG7A',
            type='video',
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        items = response['items']
        for item in items:
            if 'videoId' not in item['id']:
                print('ERROR: found entry without videoId, skipping')
                continue

            video_id = item['id']['videoId']

            if video_id in videos:
                #print(f'WARN: skipping duplicate video (in iteration {i})')
                continue

            if item['id']['kind'] != 'youtube#video':
                videos[video_id] = dict(error=f'unexpected type: {item["id"]["kind"]}')
                continue

            snippet = item['snippet']

            # Get and match title
            title = snippet['title']
            m = title_regex.match(title)
            if m is None:
                videos[video_id] = dict(
                    title=title,
                    error=f'could not match title regex',
                )
                continue

            version = m.group(1)
            sub_title = m.group(2)


            # Match original filename from description
            # If no match, check if sub title is the filename
            m = description_regex.search(snippet['description'])
            if m is not None:
                filename = m.group(1)
            elif sub_title.endswith('.rec'):
                filename = sub_title
            else:
                videos[video_id] = dict(
                    title=title,
                    version=version,
                    error=f'no original filename',
                )
                continue


            videos[video_id] = dict(
                title=title,
                version=version,
                filename=filename,
            )

        if 'nextPageToken' not in response or next_page_token == response['nextPageToken']:
            break

        i += 1
        next_page_token = response['nextPageToken']

    print(json.dumps(videos, indent=4))
    with open('videos.json', 'w') as f:
        f.write(json.dumps(videos))
        f.write('\n')


if __name__ == '__main__':
    main()
