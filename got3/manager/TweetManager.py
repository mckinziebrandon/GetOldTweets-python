import urllib.parse
import urllib.request
import urllib.error
import urllib.request
import urllib.error
import urllib.parse
import json
import re
import datetime
import sys
from http.cookiejar import CookieJar
from urllib.request import build_opener
from urllib.request import ProxyHandler, HTTPCookieProcessor
from pyquery import PyQuery

from .. import models

class TweetManager:

    def __init__(self):
        pass

    @staticmethod
    def getTweets(tweetCriteria,
                  receiveBuffer=None,
                  bufferLength=100,
                  proxy=None):

        refreshCursor = ''
        results = []
        resultsAux = []
        cookieJar = CookieJar()
        active = True

        while active:
            json = TweetManager.getJsonReponse(tweetCriteria,
                                               refreshCursor,
                                               cookieJar,
                                               proxy)

            if len(json['items_html'].strip()) == 0:
                break

            refreshCursor = json['min_position']

            # Gets a list of all elements <div class=js-stream-tweet .../>
            # (These are the individual tweet cards.)
            tweets = PyQuery(json['items_html'])('div.js-stream-tweet')

            if len(tweets) == 0:
                break

            for tweetHTML in tweets:
                tweetPQ = PyQuery(tweetHTML)
                tweet = models.Tweet()

                twitter_handle = tweetPQ("span:first.username.u-dir b").text()
                txt = re.sub(r"\s+", " ",
                        tweetPQ("p.js-tweet-text").text().replace('# ', '#').replace('@ ', '@'));
                retweets = int(tweetPQ("span.ProfileTweet-action--retweet span.ProfileTweet-actionCount")
                        .attr("data-tweet-stat-count")
                        .replace(",", ""));
                favorites = int(tweetPQ("span.ProfileTweet-action--favorite span.ProfileTweet-actionCount")
                        .attr("data-tweet-stat-count")
                        .replace(",", ""));
                dateSec = int(tweetPQ("small.time span.js-short-timestamp")
                        .attr("data-time"));
                id = tweetPQ.attr("data-tweet-id");
                permalink = tweetPQ.attr("data-permalink-path");
                user_id = int(tweetPQ("a.js-user-profile-link")
                        .attr("data-user-id"))

                receivers = tweetPQ("div.ReplyingToContextBelowAuthor span.username b").text()
                for mention in re.compile('(@\\w*)').findall(txt):
                    if mention not in receivers:
                        receivers += ' ' + mention[1:]  # Don't include the '@' symbol.

                geo = ''
                geoSpan = tweetPQ('span.Tweet-geo')
                if len(geoSpan) > 0:
                    geo = geoSpan.attr('title')
                urls = []
                for link in tweetPQ("a"):
                    try:
                        urls.append((link.attrib["data-expanded-url"]))
                    except KeyError:
                        pass

                tweet.id = id
                tweet.permalink = 'https://twitter.com' + permalink
                tweet.sender = twitter_handle
                tweet.text = txt
                tweet.date = datetime.datetime.fromtimestamp(dateSec)
                tweet.formatted_date = datetime.datetime.fromtimestamp(dateSec).strftime("%a %b %d %X +0000 %Y")
                tweet.retweets = retweets
                tweet.favorites = favorites

                # Then the handle was just mentioned (without using @sign) -- we don't care about that.
                if not receivers:
                    continue

                tweet.hashtags = " ".join(re.compile('(#\\w*)').findall(tweet.text))
                tweet.geo = geo
                tweet.urls = ",".join(urls)
                tweet.author_id = user_id
                tweet.receivers = receivers

                tweet = tweet.as_dict()
                results.append(tweet)
                resultsAux.append(tweet)

                if receiveBuffer and len(resultsAux) >= bufferLength:
                    receiveBuffer(resultsAux)
                    resultsAux = []

                if tweetCriteria.maxTweets > 0 and len(results) >= tweetCriteria.maxTweets:
                    active = False
                    break


        if receiveBuffer and len(resultsAux) > 0:
            receiveBuffer(resultsAux)

        return results

    @staticmethod
    def getJsonReponse(tweetCriteria, refreshCursor, cookieJar, proxy):
        url = "https://twitter.com/i/search/timeline?f=tweets&q=%s&src=typd&%smax_position=%s"
        urlGetData = ''
        if hasattr(tweetCriteria, 'username'):
            urlGetData += ' from:' + tweetCriteria.username

        if hasattr(tweetCriteria, 'since'):
            urlGetData += ' since:' + tweetCriteria.since

        if hasattr(tweetCriteria, 'until'):
            urlGetData += ' until:' + tweetCriteria.until

        if hasattr(tweetCriteria, 'querySearch'):
            urlGetData += ' ' + tweetCriteria.querySearch

        if hasattr(tweetCriteria, 'lang'):
            urlLang = 'lang=' + tweetCriteria.lang + '&'
        else:
            urlLang = ''

        url = url % (urllib.parse.quote(urlGetData), urlLang, refreshCursor)
        headers = [
                ('Host', "twitter.com"),
                ('User-Agent', "Mozilla/5.0 (Windows NT 6.1; Win64; x64)"),
                ('Accept', "application/json, text/javascript, */*; q=0.01"),
                ('Accept-Language', "de,en-US;q=0.7,en;q=0.3"),
                ('X-Requested-With', "XMLHttpRequest"),
                ('Referer', url),
                ('Connection', "keep-alive")]

        if proxy:
            opener = build_opener(
                    ProxyHandler({'http': proxy, 'https': proxy}),
                    HTTPCookieProcessor(cookieJar))
        else:
            opener = build_opener(HTTPCookieProcessor(cookieJar))
            opener.addheaders = headers

        try:
            response = opener.open(url)
            jsonResponse = response.read()
        except:
            #print("Twitter weird response. Try to see on browser: ", url)
            print("Twitter weird response. Try to see on browser: https://twitter.com/search?q=%s&src=typd" % urllib.parse.quote(urlGetData))
            print("Unexpected error:", sys.exc_info()[0])
            sys.exit()
            return

        dataJson = json.loads(jsonResponse.decode())
        return dataJson
