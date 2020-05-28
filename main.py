#!/usr/bin/env python3

import requests
import os
import argparse
import logging
from bs4 import BeautifulSoup
from urllib.parse import unquote

QUALITIES = ['1080p', '720p', '480p', '360p']

def upgrade_quality(q, i, id):
    q += 1
    if q >= len(QUALITIES):
        print(f'[ERROR]: no torrent found for episode {id}')
        i += 1
        q = 0
    else:
        print(f'[WARNING]: no torrent found with quality : {quality}')
        quality = QUALITIES[q]
    return q, i


def downloadFromSoup(soup, quality, directory):
    list_link = soup.find_all("div", {"class": "rls-info-container"})
    q = 0
    if quality == "best":
        quality = QUALITIES[q]

    i = 0
    while i < len(list_link):
        link = list_link[i]
        link_id = link.get('id')
        quality_line = link.find("div", {"class": "rls-link link-"+quality})
        if not quality_line:
            q, i = upgrade_quality(q, i, link_id)
            continue

        try:
            torrent_url = quality_line.find("span", {"class": "dl-type hs-torrent-link"}).find("a")['href']
        except AttributeError:
            q, i = upgrade_quality(q, i, link_id)
            continue

        try:
            r = requests.get(torrent_url)
        except requests.exceptions.MissingSchema:
            print('[ERROR]: request failed')
        else:
            filename = unquote(r.headers['Content-Disposition'].split('"')[1])
            with open(os.path.join(directory, filename), 'wb') as f:
                f.write(r.content)
            print(filename, " [OK]")
        i += 1


def main(args):
    # get variable from arparse
    url = args.url[0]
    directory = args.directory
    quality = args.quality
    # create the dir that will contains the torrent files
    if directory != '' and not os.path.isdir(directory):
        os.mkdir(directory)

    # get the content of the page
    try:
        r = requests.get(url)
    except requests.exceptions.MissingSchema:
        return 'invalid URL'
    soup = BeautifulSoup(r.content, "html5lib")

    # get the id of the anime for the api
    api_id = soup.find("div", {"class": "entry-content"}).find("script").text.split('=')[1][:-1]

    # request the api for the episode list
    i = 0
    while r.content != b'DONE':
        episode_url = "https://horriblesubs.info/api.php?method=getshows&type=show&showid=" + api_id + "&nextid=" + str(i)
        i += 1
        r = requests.get(episode_url)
        soup = BeautifulSoup(r.content, "html5lib")
        downloadFromSoup(soup, quality, directory)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
            'url', metavar='N', type=str, nargs='+',
            help='URL of the horrible subs anime'
    )
    parser.add_argument(
            '-q', '--quality', type=str, nargs='?',
            default='1080p',
            choices=QUALITIES,
    )
    parser.add_argument(
            '-d', '--directory', type=str, nargs='?',
            default='torrent',
            help='Directory to store torrent files'
    )
    args = parser.parse_args()
    main(args)
