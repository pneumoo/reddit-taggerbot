# reddit-taggerbot

These are old files from 2017 that I'm archiving. 

taggerbot.py identifes active users of a target subreddit, according to metrics defined in the script, and then formats the list so it can be used with Reddit Enhancement Suite (RES) to tag those users. By tagging the users in RES, a bright flag is placed next to the users' usernames in the browser. This allow for fast visual identification of users who are active in the target subreddit. 

This is helpful when engaging with users who may be trying to subvert a forum through any relatively covert means such as concern trolling, forum sliding, sealioning, JAQing etc. Rather than looking through the users' histories, the tag is a fast identifier that they might be a bad actor. 

False positives definitely exist, but can be reduced by changing the thresholds at the collection step in taggerbot.py. 
