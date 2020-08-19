from trello import TrelloClient
from datetime import datetime
from sys import exit, argv
from mailchimp_marketing import Client
from mailchimp_marketing.api_client import ApiClientError
from bs4 import BeautifulSoup
import markdown
from mdx_gfm import GithubFlavoredMarkdownExtension
import config


def debug_out(str):
    if config.debug:
        print("-- %s" % str)


if len(argv) != 2 or argv[1] not in ["preview", "final"]:
    print("Usage: newsletter.py [preview|final]")
    exit(1)

newsletter_type = argv[1]

def getTrelloCards():
    client = TrelloClient(
        api_key=config.api_key,
        api_secret=config.api_secret,
        token=config.token,
        token_secret=config.token_secret
    )

    org_name = config.org_name
    brd_name = config.brd_name

    list_name = datetime.now().strftime("%Y-%V")

    orgs = list(filter(lambda x: x.name == org_name,
                       client.list_organizations()))
    if len(orgs) != 1:
        print("Error while filtering organzation")
        exit(1)

    debug_out("Organization found")

    brds = list(filter(lambda x: x.name == brd_name,
                       orgs[0].get_boards("open")))
    if len(brds) != 1:
        print("Error while filtering boards")
        exit(1)

    debug_out("Board found")

    lists = list(filter(lambda x: x.name == list_name,
                        brds[0].get_lists("open")))

    if len(lists) != 1:
        print("Error while filtering lists")
        exit(1)

    cards = lists[0].list_cards()

    debug_out("List found, with %s cards" % len(cards))

    return cards


def sendNewsletter(items, newsletter_type):
    subject = datetime.now().strftime("MuMaNews - CW %V")
    title = "%s %s" % (datetime.now().strftime("%Y-%V"), newsletter_type)
    try:
        client = Client()
        client.set_config({
            "api_key": config.mailchimp_api_key,
            "server": config.mailchimp_server
        })

        response = client.campaigns.create({
            "type": "regular",
            "recipients": {
                    "list_id": config.mailchimp_list_id
            },
            "settings": {
                "template_id": config.mailchimp_template_id,
                "subject_line": subject,
                "title": title,
                "from_name": config.MAIL_FROM_NAME,
                "reply_to": config.MAIL_FROM
            }
        })
        # print(response)
        campaign_id = response["id"]
        debug_out("Mailchimp Campaign: %s / %s" % (campaign_id, response["web_id"])

        response = client.campaigns.get_content(campaign_id)
        soup = BeautifulSoup(response["html"], "html.parser")

        template_elem_src = soup.find(
            string="%TITLE%").find_parent(class_="mcnTextBlock")

        template_txt = str(template_elem_src)
        output = []
        for item in items:
            txt = template_txt.replace("%TITLE%", item.name)
            txt = txt.replace("%CONTENT%", markdown.markdown(item.description,extensions=[GithubFlavoredMarkdownExtension()]))
            output.append(txt)
        new_elem = BeautifulSoup("".join(output), "html.parser")

        template_elem_src.replace_with(new_elem)

        response = client.campaigns.set_content(campaign_id, {
            "html": str(soup)
        })

        if newsletter_type == "preview":
            response = client.campaigns.send_test_email(
                campaign_id, {"test_emails": [ config.MAIL_TO_PREVIEW ], "send_type": "html"})
            debug_out(str(response))
        else:
            response = client.campaigns.send(campaign_id)
            debug_out(str(response))

    except ApiClientError as error:
        print("Error: {}".format(error.text))


items = getTrelloCards()
sendNewsletter(items, newsletter_type)
