#!/usr/bin/env python3

import requests
import os
import argparse
import logging
from bs4 import BeautifulSoup
from urllib.parse import unquote


def downloadFromSoup(soup, quality, directory):
    list_link = soup.find_all("div", {"class": "rls-info-container"})
    for link in list_link:
        try:
            torrent = link.find("div", {"class": "rls-link link-"+quality}).find("span", {"class": "dl-type hs-torrent-link"}).find("a")['href']
            r = requests.get(torrent)
            filename = unquote(r.headers['Content-Disposition'].split('"')[1])
            with open(os.path.join(directory, filename), 'wb') as f:
                f.write(r.content)
        except requests.exceptions.MissingSchema:
            print('[ERROR]: request failed')
        else:
            print(filename, " [OK]")


def main(args):
    # get variable from arparse
    url = args.url[0]
    directory = args.directory
    quality = args.quality[0]
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
            '-q', '--quality', default="best", nargs=1,
            choices=['best', '1080p', '720p', '480p']
    )
    parser.add_argument(
            '-d', '--directory', type=str, nargs='?',
            default='torrent',
            help='Directory to store torrent files'
    )
    args = parser.parse_args()
    main(args)
