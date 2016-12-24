from flask import Flask, request
from models import Memegen, Slack, parse_text_into_params, image_exists

app = Flask(__name__)
memegen = Memegen()
slack = Slack()

@app.route("/")
def meme():
    if not request.args:
        return memegen.help()

    token = request.args["token"]
    text = request.args["text"].strip()
    channel_id = request.args["channel_id"]
    user_id = request.args["user_id"]

    if token != slack.SLASH_COMMAND_TOKEN:
        return "Unauthorized."

    if text.lower() in ("help", ""):
        return memegen.help()

    if text.lower() == "templates":
        return memegen.template_list

    template, top, bottom = parse_text_into_params(text)

    if template in memegen.valid_templates:
        meme_url = memegen.build_url(template, top, bottom)
    elif image_exists(template):
        meme_url = memegen.build_url("custom", top, bottom, template)
    else:
        return memegen.bad_template(template)

    payload = {"channel": channel_id}
    user = slack.find_user_info(user_id)
    payload.update(user)

    attachments = [{"image_url": meme_url, "fallback": "; ".join([top, bottom])}]
    payload.update({"attachments": attachments})

    try:
        slack.post_meme_to_webhook(payload)
    except Exception as e:
        return e

    return "Success!", 200
