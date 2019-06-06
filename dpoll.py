import json
import uuid
import re
from bs4 import BeautifulSoup
import requests
from steem import Steem
from steem.transactionbuilder import TransactionBuilder
from steembase import operations


website = "https://dpoll.xyz/?order=new"
response = requests.get(website)
html = response.content
soup = BeautifulSoup(html, "html.parser")
li = soup.find_all("li", {"class": "list-group-item"})
# Finding first poll . If you want to change this  try to  lopping li[]
a = li[1].findAll("a", href=True)
poolLink = "https://dpoll.xyz"+a[0].attrs['href']
responseLink = requests.get(poolLink)
htmlLink = responseLink.content
soupLink = BeautifulSoup(htmlLink, "html.parser")
bar = soupLink.find_all("div", {"role": "progressbar"})
author = a[0].attrs['href'].split("/")[2]
permlink = a[0].attrs['href'].split("/")[3]

s = Steem(keys=["<Steem Posting Key"])

# Checkig poll votes , If it is not voted before code will not vote.
if len(bar) >= 1:
    x = re.search("</form>", str(soupLink))
    y = re.search("<small><em>", str(soupLink))
    # z is firt option in poll . First option is the most voted option.
    z = str(soupLink)[x.end():y.start()]
    z = z.replace("\n", "")
    z1 = re.search("                                                                                                                        ",z)
    z2 = re.search("                                    ", z[z1.end():])
    z = z[z1.end():]
    z = z[:z2.start()]
# Checking your profile , If you have benn voted before code will not vote.
    query2 = {
        "limit": 5,  # number of comments
        "start_author": 'Your profile name'  # selected user
    }

    # get comments of selected account
    comments = s.get_discussions_by_comments(query2)
    vaziyet = False
    for i in comments:
        if i['parent_permlink'] == permlink:
            vaziyet = True

    if vaziyet == False:

        #Now code will vote . https://gist.github.com/emre/16e561b416de0e9f7fefc701e673d696

        voter = "Your Profile name"
        author = author.split('@')[1]
        poll_author = author
        poll_permlink = permlink
        votes = [
            z,
        ]

        ops = [
            operations.Comment(**{
                "author": voter,
                "body": 'Voted for \n - %s' % votes[0],
                "permlink": str(uuid.uuid4()),
                "parent_permlink": poll_permlink,
                "parent_author": poll_author,
                "json_metadata": json.dumps({
                    "content_type": "poll_vote",
                    "votes": votes,
                    "tags": ["dpoll", ]
                }),
                "title": "",
            }),
        ]

        tb = TransactionBuilder()
        tb.appendOps(ops)
        tb.appendSigner(voter, "posting")
        tb.sign()
        resp = s.broadcast_transaction_synchronous(tb)

        # trigger dpoll to register the vote it's own database
        r = requests.get("https://dpoll.xyz/web-api/sync", params={
            "block_num": resp["block_num"],
            "trx_id": resp["id"]
        })

        print(r.text)








