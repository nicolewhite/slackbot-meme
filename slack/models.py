import os
from urllib import unquote_plus, quote
import requests


class Memegen:

    def __init__(self):
        self.BASE_URL = "https://memegen.link"

    def get_templates(self):
        response = requests.get(self.BASE_URL + "/api/templates/").json()

        data = []

        for key, value in response.items():
            link_response = link_requests.get(value).json()
            name = value.replace(self.BASE_URL + "/api/templates/", "")
            description = key
            link_unicode = link_response["description"]
            link = link_unicode.encode('utf-8')
            data.append((name, description, link))

        data.sort(key=lambda tup: tup[0])
        return data

    def list_templates(self):
        templates = self.get_templates()

        help = ""

        for template in templates:
            help += "`{0}` {1}` {2}\n".format(template[0], template[1], template[2])

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
