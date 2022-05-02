import os

from fake_useragent import UserAgent
import requests
from datetime import datetime
import csv


ua = UserAgent()


def fetch_tweets(file, q, cursor=None):

    headers = {
        'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
        'User-Agent': ua.ie
    }
    guest_token = requests.post('https://api.twitter.com/1.1/guest/activate.json', headers=headers).json()[
        "guest_token"]

    headers = {
        'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
        'x-guest-token': guest_token,
        'User-Agent': ua.ie
    }

    params = [
        ('include_profile_interstitial_type', '1'),
        ('include_blocking', '1'),
        ('include_blocked_by', '1'),
        ('include_followed_by', '1'),
        ('include_want_retweets', '1'),
        ('include_mute_edge', '1'),
        ('include_can_dm', '1'),
        ('include_can_media_tag', '1'),
        ('include_ext_has_nft_avatar', '1'),
        ('skip_status', '1'),
        ('cards_platform', 'Web-12'),
        ('include_cards', '1'),
        ('include_ext_alt_text', 'true'),
        ('include_quote_count', 'true'),
        ('include_reply_count', '1'),
        ('tweet_mode', 'extended'),
        ('include_entities', 'true'),
        ('include_user_entities', 'true'),
        ('include_ext_media_color', 'true'),
        ('include_ext_media_availability', 'true'),
        ('include_ext_sensitive_media_warning', 'true'),
        ('include_ext_trusted_friends_metadata', 'true'),
        ('send_error_codes', 'true'),
        ('simple_quoted_tweet', 'true'),
        ('q', q),
        ('tweet_search_mode', 'live'),
        ('count', '20'),
        ('query_source', 'typed_query'),
        ('pc', '1'),
        ('spelling_corrections', '1'),
        ('ext', 'mediaStats,highlightedLabel,hasNftAvatar,voiceInfo,enrichments,superFollowMetadata,unmentionInfo'),
    ]
    if cursor:
        params.append(("cursor", cursor))

    data = requests.get('https://twitter.com/i/api/2/search/adaptive.json', headers=headers, params=params).json()
    tweets = data['globalObjects']['tweets']
    users = data['globalObjects']['users']

    rows = []
    for k, tweet in tweets.items():
        created_at = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        user = users[tweet['user_id_str']]
        row = [
            tweet['conversation_id_str'],
            created_at,
            tweet['retweet_count'],
            tweet['reply_count'],
            tweet['favorite_count'],
            user['screen_name'],
            user['followers_count'],
            user['friends_count'],
            tweet['full_text'],
        ]
        rows.append(row)

    rows.sort(key=lambda ob: ob[1], reverse=True)

    with open(file, "a") as f:
        f.seek(0, os.SEEK_END)
        writer = csv.writer(f)
        if f.tell() < 1:  # if file empty
            writer.writerow(['tweet_id', 'created_at', 'retweet_count', 'reply_count', 'favorite_count', 'user_name', 'followers_count', 'following_count', 'text'])
        writer.writerows(rows)

    print("fetched %s" % len(rows))
    print("fetching next")

    try:
        next_cursor = get_next_cursor(data)
        if next_cursor and len(rows):
            fetch_tweets(file, q, next_cursor)
    except KeyError as e:
        print("No more")


def get_next_cursor(data):
    instructions = data['timeline']['instructions']
    for ins in instructions:
        if "addEntries" in ins:
            entries = ins['addEntries']['entries']
            for entry in entries:
                if entry['entryId'] == "sq-cursor-bottom":
                    return entry['content']['operation']['cursor']['value']
        elif "replaceEntry" in ins:
            if ins['replaceEntry']['entry']['entryId'] == "sq-cursor-bottom":
                return ins['replaceEntry']['entry']['content']['operation']['cursor']['value']
    return None


if __name__ == '__main__':
    fetch_tweets("data/multiplayer2021.csv", "(#multiplayeronline) until:2021-05-31 since:2019-03-01", None)
