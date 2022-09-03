import os
import interactions
from query import (
    retrieve_ASAs,
    ASA_overview,
    reddit_post_overview,
    reddit_post_more,
    twitter_overview,
    twitter_analytics,
    github_overview,
    github_per_repo,
    github_per_time,
)


bot = interactions.Client(token=os.environ.get(BOT_TOKEN))


ENDING_NOTE = (
    "Thank you! Check out https://asalytics.ai/ to conduct more detailed analysis."
)


### * BUTTONS *
button1 = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Twitter",
    custom_id="twitter",
)

button2 = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Reddit",
    custom_id="reddit",
)

button3 = interactions.Button(
    style=interactions.ButtonStyle.PRIMARY,
    label="Github",
    custom_id="github",
)


button11 = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Likes",
    custom_id="likes",
)

button12 = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Retweets",
    custom_id="rt",
)

button13 = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Sentiment",
    custom_id="score",
)

button21 = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="More on this post",
    custom_id="more",
)

button22 = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="Next post",
    custom_id="next",
)

button31 = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="PerRepo",
    custom_id="perrepo",
)

button32 = interactions.Button(
    style=interactions.ButtonStyle.SUCCESS,
    label="PerTime",
    custom_id="pertime",
)


### * ACTIONROWS *
row_base = interactions.ActionRow(components=[button1, button2, button3])
row_twitter = interactions.ActionRow(components=[button11, button12, button13])
row_reddit_a = interactions.ActionRow(components=[button21, button22])
row_reddit_b = interactions.ActionRow(components=[button22])
row_github = interactions.ActionRow(components=[button31, button32])


### * RETRIEVING ASAs names and unitnames, and creating hashtables for them*
asa_details = retrieve_ASAs()
asa_name_table = dict(map(lambda x: (x["name"].lower(), x["assetId"]), asa_details))
asa_unit1_table = dict(
    map(lambda x: (x["unitname1"].lower(), x["assetId"]), asa_details)
)
asa_general_table = dict(
    map(
        lambda x: (x["assetId"], (x["name"], x["unitname1"], x["available"])),
        asa_details,
    )
)

## * COMMANDS for display *
@bot.command()
async def asalytics(ctx: interactions.CommandContext, *args, **kwargs):
    pass


@asalytics.subcommand()
async def see_asalist(ctx: interactions.CommandContext):
    """Check here to see the list of assets in my database."""
    giant_string = ""
    giant_string += "List of ASAs in our database:\nASA Name\tUnit Name\tSocial Media Data Availability\n"
    for asa in asa_general_table.values():
        if len(giant_string) > 1800:
            await ctx.send(giant_string)
            giant_string = ""
        for row in asa:
            giant_string += str(row) + "\t\t"
        giant_string += "\n"

    giant_string += "\nNow feel free to retrieve analytics for any of the above assets using either its name or its unit name."
    await ctx.send(giant_string)


@asalytics.subcommand()
@interactions.option(description="Input ASA name")
async def get_analytics(ctx: interactions.CommandContext, asset_name: str):
    """Hey! I give social insight for crypto assets. What asset do you want to analyze?"""
    global specific_ASA, ASA_ID
    specific_ASA = asset_name
    if asset_name.lower() in asa_name_table or asset_name.lower() in asa_unit1_table:
        ASA_ID = asa_name_table.get(asset_name.lower())
        if not ASA_ID:
            ASA_ID = asa_unit1_table.get(asset_name.lower())
        await ctx.send(
            f"Hi {ctx.author}, retrieving data for {asset_name}...\n{ASA_overview(ASA_ID)}"
        )
        if not asa_general_table.get(ASA_ID)[2]:  # check if available is False
            await ctx.send(
                f"I don't have social media data for {asset_name} yet. But my creators are working hard to make it available ASAP."
            )
        else:
            await ctx.send(
                "I also have access to Twitter, Reddit and Github data. Which would you like to see first?\n",
                components=row_base,
            )  # Editing this later to account for Available data vs Unavailable data
            global reddit_post_data
            reddit_post_data = reddit_post_overview(
                ASA_ID
            )  # initializing the reddit kini here because it is a generator function
    else:
        await ctx.send(
            f"{asset_name} not found in the ASA database. Crosscheck the name and/or check out https://asalytics.ai/ for detailed analytics."
        )


### * Button Actions*
@bot.component("twitter")
async def button1_response(ctx):
    result = twitter_overview(ASA_ID)
    await ctx.send(f"{specific_ASA} has:\n{result}")
    await ctx.send(f"Explore more about {specific_ASA}?", components=row_twitter)


@bot.component("likes")
async def button11_response(ctx):
    result = twitter_analytics(ASA_ID, "likes")
    await ctx.send(
        f"Detailed information about {specific_ASA}'s Twitter Likes data:\n{result}"
    )
    await ctx.send("You can restart to check other forms of analytics.")


@bot.component("rt")
async def button12_response(ctx):
    result = twitter_analytics(ASA_ID, "retweets")
    await ctx.send(
        f"Detailed information about {specific_ASA}'s Twitter Retweets data:\n{result}"
    )
    await ctx.send("You can restart to check other forms of analytics.")


@bot.component("score")
async def button13_response(ctx):
    result = twitter_analytics(ASA_ID, "sentiment")
    await ctx.send(
        f"Detailed information about Twitter people's sentiment on {specific_ASA}:\n{result}"
    )
    await ctx.send("You can restart to check other forms of analytics.")


@bot.component("reddit")
async def button2_response(ctx):
    await ctx.send(
        f"Here are key analytics of some {specific_ASA}'s hot posts on Reddit:\n{next(reddit_post_data)}",
        components=row_reddit_a,
    )


@bot.component("more")
async def button21_response(ctx):
    await ctx.send(reddit_post_more(ASA_ID), components=row_reddit_b)


@bot.component("next")
async def button22_response(ctx):
    try:
        await ctx.send(
            f"Here is another:\n{next(reddit_post_data)}",
            components=row_reddit_a,
        )
    except:
        await ctx.send(ENDING_NOTE)


@bot.component("github")
async def button3_response(ctx):
    await ctx.send(
        f"The {specific_ASA} asset has the following GitHub data summary:\n{github_overview(ASA_ID)}"
    )
    await ctx.send("Check out more detailed analysis:\n", components=row_github)


@bot.component("perrepo")
async def button31_response(ctx):
    await ctx.send(
        str(github_per_repo(ASA_ID))[:2000]
    )  # interpreting it as a string for now, need a finer response style
    await ctx.send(ENDING_NOTE)


@bot.component("pertime")
async def button32_response(ctx):
    await ctx.send(
        str(github_per_time(ASA_ID))
    )  # interpreting it as a string for now, need a finer response style
    await ctx.send(ENDING_NOTE)


bot.start()
