Readme for "last 5 mins" Twitter Project

Purpose:
> To automatically check for and download new tweets @ a particular user in 5 min increments.
> If tweets are found to contain key phrases indicating a potential technical issue, relevant tweets are bundled together and automatically sent as an email for review.
> This would be a good setup to monitor live streams or performance of any service that may have outages affecting end users.

Steps:
1 > Set up twitter dev account with enhanced permissions to make use of twitter api.
2 > Create config.ini file to contain api_keys and access_tokens (so they won't need to be explcitly mentioned in uploaded code).
    [twitter]

    api_key = blah
    api_key_secret = blah

    access_token = blah
    access_token_secret = blah

NOTE:
Running code for script "twitter_api_last_5_mins" ad-hoc will download/email tweets.
Now we want to automate the script being run every 5 minutes.
To do this, we will use Task Scheduler (on Windows).

3 > Create a task 
    >> On general tab: make sure "configure for" is set to Windows 10
    >> On triggers tab: set up trigger with whatever schedule we want (make sure start time is in the future)
    >> On actions tab:
       >>> "action:" should be "start a program"
       >>> "Program/script:" should be the python.exe for wherever Python is installed
       >>> "Add arguments" should be the script you want to run
       >>> "Start in" should be the location for the script being run
    >> Conditions, settings, history tab: check these and make any changes you need to
4 > Once set up, an instance of cmd will now run every 5 minutes (or whatever schedule you specified) and execute the script.
