from flask import Flask, render_template
from datetime import datetime, timedelta
import pytz
import yaml
import os
import re


from modules import load_modules

app = Flask(__name__)


for module, module_name in load_modules():
    try:
        app.register_blueprint(module, url_prefix=f"/{module_name}")
    except Exception as e:
        print(f"An error occured while trying to load {module} as a blueprint: {e}")


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


@app.context_processor
def inject_globals():
    return {"global": {"compname": "Barium"}}



@app.route("/")
def homepage():
    article_list = []

    def format_date(dt_input):
        now = datetime.now(pytz.timezone("Europe/Amsterdam"))
        if dt_input.date() == now.date():
            formatted = f"Today, {dt_input.strftime('%H:%M:%S')}"
        elif dt_input.date() == (now.date() - timedelta(days=1)):
            formatted = f"Yesterday, {dt_input.strftime('%H:%M:%S')}"
        else:
            if dt_input.year == now.year:
                formatted = dt_input.strftime("%a %d %b, %H:%M:%S")
            else:
                formatted = dt_input.strftime("%a %d %b %Y, %H:%M:%S")
        return formatted

    for article in os.listdir(os.path.join(BASE_DIR, "articles", "news")):
        article_id = article.removesuffix(".md")
        with open(os.path.join(BASE_DIR, "articles", "news", article), encoding="utf-8") as file:
            article_content = file.read().strip()
        extract = re.match(r"^---\n(.*?)\n---\n", article_content, re.DOTALL)
        article_data = yaml.safe_load(extract.group(1))

        article_data["cover"] = f"/static/assets/images/{article_id}.jpg"
        article_data["url"] = f"/article/{article_id}"
        article_data["datetime_formatted"] = format_date(datetime.fromisoformat(str(article_data["datetime"])))

        article_list.append(article_data)

    return render_template("index.html", article_list = article_list)


if __name__ == "__main__":
    app.run(debug=True, port=2000)