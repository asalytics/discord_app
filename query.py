import requests, json, math


URL = "http://analytics-api.herokuapp.com/analytics"


def retrieve_ASAs():
    query = """query {
         asalist {
            result {
                available
                name
                assetId
                unitname1
            }
        }
    }"""
    r = requests.post(URL, json={"query": query})
    return json.loads(r.text)["data"]["asalist"]["result"]


def ASA_overview(asset_id):
    query = """query {
        asaData(asaID: "%s") {
            result {
                circSupply
                usdValue
                totalSupply
                fractionDecimals
            }
        }
    }""" % (
        asset_id
    )
    r = requests.post(URL, json={"query": query})
    result = json.loads(r.text)["data"]["asaData"]["result"][0]

    millnames = ["", "Thousand", "M", "B", "T"]

    def millify(n):
        n = float(n)
        millidx = max(
            0,
            min(
                len(millnames) - 1,
                int(math.floor(0 if n == 0 else math.log10(abs(n)) / 3)),
            ),
        )

        return "{:.0f}{}".format(n / 10 ** (3 * millidx), millnames[millidx])

    if not all(result.values()):
        return result
    return f"\tValue: ${round(float(result['usdValue']), 6)}\n\
    Total Supply: {millify(int(result['totalSupply'][:-result['fractionDecimals']]))}\n\
    Circ. Supply: {millify(int(result['circSupply'][:-result['fractionDecimals']]))}"


def reddit_post_overview(asset_id):
    query = """query {
        redditAnalytics(asaID: "%s", startDate: "2021-01-01") {
            postTitle
            postText
            score
            sentimentScore
            numOfComments
        }
    }""" % (
        asset_id
    )
    r = requests.post(URL, json={"query": query})
    result = json.loads(r.text)["data"]["redditAnalytics"]
    for post in result:
        yield post  ### print next step would be included in the button function.


def reddit_post_more(asset_id):
    return "Check out asalytics.ai for more imformation concerning the post and its comments."


def twitter_overview(asset_id):
    query = """query {
        twitterOverview(asaID: "%s") {
            likeTotal
            retweetTotal
            sentimentTotal
            tweetTotal
        }
    }""" % (
        asset_id
    )
    r = requests.post(URL, json={"query": query})
    result = json.loads(r.text)["data"]["twitterOverview"]
    return f"\tTotal Tweets: {result['tweetTotal']}\n\
    Total Likes: {result['likeTotal']}\n\
    Total Retweets: {result['retweetTotal']}\n\
    Average Sentiment: {result['sentimentTotal']}"


def twitter_analytics(asset_id, analyze="likes", timedate="weekday"):
    """
    analyze     either of `likes`, `retweets`, or `sentiment`
    timedate         either of `weekday`, `hour`, or `postedAt`
    """
    if timedate == "postedAt":
        query = """query {
            twitterAnalytics(asaID: "%s", weekday: false, startDate: "2021-01-01") {
                results {
                    %s
                    postedAt
                }
            }   
        }""" % (
            asset_id,
            analyze,
        )
    else:
        query = """query {
            twitterAnalytics(asaID: "%s", %s: true, startDate: "2021-01-01") {
                results {
                    %s
                    %s
                }
            }   
        }""" % (
            asset_id,
            timedate,
            analyze,
            timedate,
        )
    r = requests.post(URL, json={"query": query})
    result = json.loads(r.text)["data"]["twitterAnalytics"]["results"]
    return result


def github_overview(asset_id):
    query = """query {
        githubOverview(asaID: "%s") {
            commits
            contributors
            forks
            issues
            languages
            pullRequests
            stars
            watches
        }
    }""" % (
        asset_id
    )
    r = requests.post(URL, json={"query": query})
    result = json.loads(r.text)["data"]["githubOverview"]
    return f"\tTotal Commits: {result['commits']}\n\
    Total Contributors: {result['contributors']}\n\
    Forks: {result['forks']}\n\
    Issues: {result['issues']}\n\
    Languages Used: {', '.join(list(filter(lambda item: item is not None, result['languages'])))}\n\
    Number of Pull Requests: {result['pullRequests']}\n\
    Total Stars: {result['stars']}\n\
    Number of Watches: {result['watches']}"


def github_per_repo(asset_id, sortBy="commits"):
    query = """query {
        githubAnalyticsPerepo(asaID: "%s", sortBy: "%s") {
            repo {
                commits
                contributors
                issues
                forks
                pullRequests
                repoName
                watches
                stars
            }
        }
    }""" % (
        asset_id,
        sortBy,
    )
    r = requests.post(URL, json={"query": query})
    result = json.loads(r.text)["data"]["githubAnalyticsPerepo"]["repo"]
    return result


def github_per_time(asset_id, day="weekDay"):
    """
    params
        asset_id
        day         `weekDay` or `day`
    """
    query = """query {
        githubAnalyticsPertime(asaID: "%s", startDate: "2021-01-01", %s: true) {
            repo {
                commits
                lastPushDate
                lastPushDateDay
                lastPushDateWeekday
                stars
                pullRequests
                watches
                issues
                forks
            }
        }
    }""" % (
        asset_id,
        day,
    )
    r = requests.post(URL, json={"query": query})
    result = json.loads(r.text)["data"]["githubAnalyticsPertime"]["repo"]
    return result
