import interactions
from query import (
    retrieve_ASAs,
    ASA_overview,
    reddit_post_overview,
)
from button import row_base


bot = interactions.Client(
    token="MTAwNTkyNjQzMjc2MzAzOTc4Ng.G-gTfI.ijLHmyH9-GP6ZiDKGEob1paVrXc62Z9Gz0cCRQ",
    # default_scope=False,
)


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
    """Check here to see the list of assets in my database"""
    giant_string = ""
    giant_string += "List of ASAs in our database:\nASA Name\tUnit Name\tSocial Media Data Availability\n"
    for asa in asa_general_table.values():
        if len(giant_string) > 1800:
            await ctx.send(giant_string)
            giant_string = ""
        for row in asa:
            giant_string += str(row) + "\t\t"
        giant_string += "\n"

    giant_string += "\nNow feel free to retrieve analytics for any of the above assets using either its name or its unitname."
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
                "I don't have social media data for {asset_name} yet. But my creators are working hard to make it available ASAP"
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


bot.start()
