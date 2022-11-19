function tweepi --argument user
    open "https://tweepi.com/app/#!/grid/follow-followers/$user?_page=1&_pp=20&f0=followers_count,numeric,lt,500&f1=is_protected,boolean,eq,false&f2=follower_or_following,list,contain,neither&f3=last_tweet_time,date,gt,25&f4=member_since,date,lt,300&f5=statuses_count,numeric,gt,1500"
end
