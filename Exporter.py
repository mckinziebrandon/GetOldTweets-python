# -*- coding: utf-8 -*-
import csv
import sys
import getopt
import datetime
import codecs
import got3
from got3.globals import DEFAULT_ATTRIBUTES

DEFAULT_FILENAME = 'output_got.csv'

def main(argv):

    if len(argv) == 0:
        print('You must pass some parameters. Use \"-h\" to help.')
        return

    if len(argv) == 1 and argv[0] == '-h':
        f = open('exporter_help_text.txt', 'r')
        print(f.read())
        f.close()

        return

    try:
        opts, args = getopt.getopt(argv, "", (
            "username=", "near=", "within=", "since=", "until=",
            "querysearch=", "toptweets", "maxtweets=", "output="))

        tweetCriteria = got3.manager.TweetCriteria()
        outputFileName = DEFAULT_FILENAME

        for opt, arg in opts:
            if opt == '--username':
                tweetCriteria.username = arg
            elif opt == '--since':
                tweetCriteria.since = arg
            elif opt == '--until':
                tweetCriteria.until = arg
            elif opt == '--querysearch':
                tweetCriteria.querySearch = arg
            elif opt == '--toptweets':
                tweetCriteria.topTweets = True
            elif opt == '--maxtweets':
                tweetCriteria.maxTweets = int(arg)
            elif opt == '--near':
                tweetCriteria.near = '"' + arg + '"'
            elif opt == '--within':
                tweetCriteria.within = '"' + arg + '"'
            elif opt == '--within':
                tweetCriteria.within = '"' + arg + '"'
            elif opt == '--output':
                outputFileName = arg

        # Note: w+ better than w, because w will fail if the file already exists.
        with open(outputFileName, 'w+', encoding='utf-8', newline='') as outputFile:

            writer = csv.DictWriter(
                outputFile,
                fieldnames=DEFAULT_ATTRIBUTES,
                delimiter=',')
            writer.writeheader()

            print('Searching...\n')
            def receiveBuffer(tweets):
                for t in tweets:
                    writer.writerow(t)
            got3.manager.TweetManager.getTweets(tweetCriteria, receiveBuffer)

    except arg:
        print('Arguments parser error, try -h' + arg)
    finally:
        outputFile.close()
        print('Done. Output file generated "%s".' % outputFileName)


if __name__ == '__main__':
    main(sys.argv[1:])
