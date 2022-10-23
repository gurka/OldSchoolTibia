import os
import json
import re
import sys

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
        request = youtube.playlistItems().list(
            part='snippet',
            playlistId='UULvAMwZjm9aUUeJ-wVDMG7A',
            maxResults=50,
            pageToken=next_page_token,
        )
        response = request.execute()

        videos_saved = len(videos)
        response_items = len(response['items'])
        total_results = response['pageInfo']['totalResults']
        results_per_page = response['pageInfo']['resultsPerPage']
        print(f'Videos saved: {videos_saved}, items in response: {response_items}, total results: {total_results}, results per page: {results_per_page}')

        items = response['items']
        for item in items:
            snippet = item['snippet']
            video_id = snippet['resourceId']['videoId']

            if video_id in videos:
                print(f'WARN: skipping duplicate video (in iteration {i})')
                continue

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
                # Do another request, in case the filename has been
                # added but search index not updated yet
                request2 = youtube.videos().list(
                    part='snippet',
                    id=video_id,
                )
                response2 = request2.execute()
                item2 = response2['items'][0]
                snippet2 = item2['snippet']
                m2 = description_regex.search(snippet2['description'])
                if m2 is not None:
                    filename = m2.group(1)
                else:
                    videos[video_id] = dict(
                        title=title,
                        version=version,
                        error=f'no original filename',
                    )
                    print(json.dumps(item, indent=4))
                    continue

            # Split filename if it's something like 'foo" & "bar'
            filenames = [filename.replace('"', '') for filename in filename.split(' & ')]

            videos[video_id] = dict(
                title=title,
                version=version,
                filenames=filenames,
            )

        if 'nextPageToken' not in response or next_page_token == response['nextPageToken']:
            break

        i += 1
        next_page_token = response['nextPageToken']

    videos_saved = len(videos)
    print(f'Videos saved: {videos_saved}')

    print('Writing videos.json')
    with open('videos.json', 'w') as f:
        f.write(json.dumps(videos))
        f.write('\n')

    print('Writing videos.csv')
    with open('videos.csv', 'w') as f:
        for video_id in videos:
            video = videos[video_id]

            title = video.get('title', '')
            version = video.get('version', '')
            filenames = video.get('filenames', '')
            error = video.get('error', '')

            for filename in filenames:
                # filename must be first for VLOOKUP in Google Sheets to work
                f.write(f'{filename}\t{video_id}\t{title}\t{version}\t{error}\n')



if __name__ == '__main__':
    main()
