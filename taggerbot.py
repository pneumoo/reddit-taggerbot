# -*- coding: utf-8 -*-
"""
Created on Sat Dec 24 15:59:15 2016

@author: Brian

This tool finds active users of a subreddit and logs them so they can be 
tagged in Reddit Enhancement Suite (RES). 

An existing user tag file can be read in. This tag file can be cleaned and/or
added to on a new search. 

It's good to run this every so often as the active usernames in a subreddit
change over time.
"""


import praw
from praw.models import MoreComments
import json
import csv


# RESStorage update RESmodules.userTagger.tags
USERAGENT = 'USERAGENT'
CLIENT_ID = 'CLIENT_ID'
CLIENT_SECRET = 'CLIENT_SECRET'
USERNAME = 'USERNAME'
PASSWORD = 'PASSWORD'


# ========== Script options ==========
cleantagsflag = 0 # will clean tags if = 1, won't if = 0
subredditnames = ["The_Donald"] # lowest priority first
tagfilename = "TD_40_10-sub_com-5-20-17.txt"
tagname = "TD"        # Tag text (lowest priority first)
color = "red"       # Color of tag
sublimit = 500     # How many submissions to examine
subscorelim = 40     # Minimum score required to add submission author
comscorelim = 10    # Minimum score required to add comment author
userignore = ["AutoModerator", "publicmodlogs", "rarchives",
              "roger_bot", "moderator-bot", "TotesMessenger", "gifv-bot",
              "TotesMessenger", "autotldr"]


# Open (re-open) tagfile to read in fresh dictionary
with open(tagfilename) as tag_data:
    try:
        tags = json.load(tag_data)
    except:
        print("No existing json... creating new tag dictionary...")
        tags = {}


reddit = praw.Reddit(user_agent=USERAGENT,
                     client_id=CLIENT_ID, 
                     client_secret=CLIENT_SECRET,
                     username=USERNAME, 
                     password=PASSWORD)

# Currently inputting a redditor OBJECT
# does not distinguish between Suspended and Deleted
def userName_Exists(user):
    exists = True
    try:
        user.fullname
    except:
        exists = False
    return exists


# Searches through tagsdict to find suspended or deleted accts
# Removes these from the list and returns the "cleaned" tag dict
def cleanTags(tags):
    poplist = []
    count = 0
    length = len(tags)
    print("Searching for suspended or deleted users... TAKES A WHILE")
    for i in tags.keys():
        count += 1
        print("Searched " + str(count) + " users out of " + str(length))
        try:
            reddit.redditor(i).fullname
            continue
        except:
            poplist.append(i)
            print("popped " + i)
    
    print("Removing suspended or deleted users..")
    for i in poplist:
        tags.pop(i)
    
    return tags



def getUsers(tags, reddit):
    # Cleans the tags if we tell it to
    if cleantagsflag == 1:
        tags = cleanTags(tags)
        
    # Loop through all the subreddits in <subredditnames>    
    for index, subredditname in enumerate(subredditnames):
        print("Searching through ", sublimit, " posts on ", subredditname)
        print("Currently ", len(tags), " users tagged.")
        print()
        
        # Get subreddit object for each submission
        subreddit=reddit.subreddit(subredditname)
        
        # For each submission (qty = sublimit), examine to find author
        count = 1 
        for submission in subreddit.hot(limit = sublimit):
            # get the submissions entire CommentForest    
            submission.comments.replace_more(limit=0)
            commentlist = submission.comments.list()
            print()
            print("Searching submission " + str(count))
            print("Total comments found: " + str(len(commentlist)))
            print()
            count += 1
            
            # Only add author if the Submission score >= subscorelim            
            if  (str(submission.author).lower() not in tags.keys()) and (str(submission.author) not in userignore):
                if submission.score >= subscorelim and userName_Exists(submission.author):
                    tags["tag." + str(submission.author).lower()] = {'color': color, 'tag': tagname}
                    print("Added submitter: " + str(submission.author))
    #        else:
    #            print("User already capture or in ignore list")
    
            # Only add author if the Comment score >= comscorelim               
            for i in commentlist:
                if isinstance(i, MoreComments): # Ignore "MoreComments" links
                    continue
                if (str(i.author).lower() not in tags.keys()) and (str(i.author) not in userignore):
                    if (i.score >= comscorelim) and (userName_Exists(i.author)):
                        tags["tag." + str(i.author).lower()] = {'color': color, 'tag': tagname}
                        print("Added commenter: " + str(i.author))
    #            else:
    #                print("User already capture or in ignore list")   
        
        # Be sure to include tagging the Mods of these subs
        for mod in subreddit.moderator:
            if (mod.name not in userignore) and (userName_Exists(mod)):
                tags["tag." + mod.name.lower()] = {'color': color, 'tag': "mod " + tagname}        
                print("Added moderator: " + str(mod.name))
    
    
    # Write to file after every subreddit is searched
    with open(tagfilename, 'w') as outfile:
        json.dump(tags, outfile)
        
    return tags


def tags2csv(tags=tags,tagfilename=tagfilename):
    with open(tagfilename + "_csv", 'w') as myfile:
        userlist = []
        for user in tags.keys():
            userlist.append(user[4:])
        wr = csv.writer(myfile)
        wr.writerow(userlist)


