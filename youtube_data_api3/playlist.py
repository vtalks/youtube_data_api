import requests

from urllib.parse import urlsplit
from urllib.parse import parse_qs


def get_playlist_youtube_url(playlist_code):
    """ Get the Youtube Playlist URL given its code

    Example:
        https://www.youtube.com/playlist?list=PLuMK2S9sZg71QqVzwepG-bLBxcJWEzcW9
        must return:
        PLuMK2S9sZg71QqVzwepG-bLBxcJWEzcW9
    """
    return "https://www.youtube.com/playlist?list={:s}".format(playlist_code)


def get_playlist_code(url):
    """ Parse a Youtube Playlist URL and get its code

    Example:
        https://www.youtube.com/playlist?list=PLuMK2S9sZg71QqVzwepG-bLBxcJWEzcW9
        must return:
        PLuMK2S9sZg71QqVzwepG-bLBxcJWEzcW9
    """
    query = urlsplit(url).query
    params = parse_qs(query)
    if "list" not in params:
        raise Exception('Invalid url "%s"' % url)
    playlist_code = params["list"][0]
    return playlist_code


def fetch_playlist_data(youtube_api_key, playlist_code):
    channel_url = "https://www.googleapis.com/youtube/v3/playlists"
    payload = {'id': playlist_code,
               'part': 'snippet,contentDetails',
               'key': youtube_api_key}
    resp = requests.get(channel_url, params=payload)
    if resp.status_code != 200:
        raise Exception(
            'Error fetching playlist data "%s"' % resp.status_code)
    response_json = resp.json()
    channel_data = None
    if len(response_json["items"]) > 0:
        channel_data = response_json["items"][0]
    return channel_data


def fetch_playlist_page_items(youtube_api_key, playlist_code, page_token):
    videos_id_list = []

    channel_url = "https://www.googleapis.com/youtube/v3/playlistItems"
    payload = {'playlistId': playlist_code,
               'maxResults': 50,
               'part': 'snippet',
               'key': youtube_api_key,
               'pageToken': page_token}
    resp = requests.get(channel_url, params=payload)
    if resp.status_code != 200:
        if resp.status_code == 404:
            return []
        else:
            raise Exception(
                'Error fetching playlist items "%s"' % resp.status_code)
    response_json = resp.json()
    data_json = response_json["items"]
    for item in data_json:
        videos_id_list.append(item["snippet"]["resourceId"]["videoId"])

    return response_json, videos_id_list


def fetch_playlist_items(youtube_api_key, playlist_code):
    channel_url = "https://www.googleapis.com/youtube/v3/playlistItems"
    payload = {'playlistId': playlist_code,
               'maxResults': 50,
               'part': 'snippet',
               'key': youtube_api_key}
    resp = requests.get(channel_url, params=payload)
    if resp.status_code != 200:
        if resp.status_code == 404:
            return []
        else:
            raise Exception('Error fetching playlist items "%s"' % resp.status_code)
    response_json = resp.json()
    videos_id_list = []
    data_json = response_json["items"]
    for item in data_json:
        videos_id_list.append(item["snippet"]["resourceId"]["videoId"])

    while 'nextPageToken' in response_json:
        response_json, videos_pageid_list = fetch_playlist_page_items(youtube_api_key, playlist_code, response_json['nextPageToken'])
        videos_id_list += videos_pageid_list

    return videos_id_list
