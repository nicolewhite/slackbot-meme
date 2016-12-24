import os
from urllib import unquote_plus, quote
import requests


class Memegen:

    def __init__(self):
        self.BASE_URL = "https://memegen.link"
        self.template_info = self.get_template_info()
        self.valid_templates = self.get_valid_templates()
        self.template_list = self.get_template_list()

    def get_valid_templates(self):
        return [x[0] for x in self.template_info]

    def get_template_info(self):
        template = requests.get(self.BASE_URL + "/api/templates/").json()

        data = []

        for description, api_link in template.items():
            alias = api_link.split("/api/templates/")[1]
            link = "https://memegen.link/{}/your-text/goes-here.jpg".format(alias)

            alias = alias.encode('utf8')
            description = description.encode('utf8')
            link = link.encode('utf8')

            data.append((alias, description, link))

        return sorted(data, key=lambda x: x[0])

    def get_template_list(self):
        help = ""

        for alias, description, example_link in self.template_info:
            help += '`<{}|{}>` {}\n'.format(example_link, alias, description)

        return help

    def build_url(self, template, top, bottom, alt=None):
        path = "/{0}/{1}/{2}.jpg".format(template, top or '_', bottom or '_')

        if alt:
            path += "?alt={}".format(alt)

        url = self.BASE_URL + path

        return url

    def bad_template(self, template):
        return ("Template `%s` doesn't exist. "
                "Type `/meme templates` to see valid templates "
                "or provide your own as a URL." % template)

    def help(self):
        return "\n".join([
            "Welcome to Slack Meme!",
            'Check me out on <https://github.com/nicolewhite/slack-meme|GitHub>.',
            "**> Commands:**",
            "* `/meme template_name;top_row;bottom_row` generate a meme",
            "    (NOTE: template_name can also be a URL to an image)",
            "* `/meme templates` View templates",
            "* `/meme help` Shows this menu"
        ])


def image_exists(path):
    if path.split("://")[0] not in ["http", "https"]:
        return False

    r = requests.head(path)
    return r.status_code == requests.codes.ok


class Slack:

    def __init__(self):
        self.BASE_URL = "https://slack.com/api"
        self.API_TOKEN = os.environ.get("SLACK_API_TOKEN")
        self.WEBHOOK_URL = os.environ.get("SLACK_WEBHOOK_URL").strip()
        self.SLASH_COMMAND_TOKEN = os.environ.get("SLACK_SLASH_COMMAND_TOKEN")

    def find_user_info(self, user_id):
        url = self.BASE_URL + "/users.info?token={0}&user={1}".format(self.API_TOKEN, user_id)
        response = requests.get(url)

        user = response.json()["user"]
        username = user["name"]
        icon_url = user["profile"]["image_48"]

        return {"username": username, "icon_url": icon_url}

    def post_meme_to_webhook(self, payload):
        requests.post(self.WEBHOOK_URL, json=payload)


def parse_text_into_params(text):
    text = unquote_plus(text).strip()
    text = text[:-1] if text[-1] == ";" else text

    params = text.split(";")

    template = params[0].strip()
    del params[0]

    params = [x.strip() for x in params]
    params = [x.replace(" ", "_") for x in params]
    params = [quote(x.encode("utf8")) for x in params]

    params += [None] * (2 - len(params))
    return template, params[0], params[1]
