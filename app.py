# import quart_flask_patch
from quart import Quart, request, globals, redirect, url_for, render_template
from models import user_dal, Base, engine
import os
from forms import UserForm
import aiohttp
from aiohttp import BasicAuth
from quart_auth import (
    login_required,
    login_user,
    logout_user,
    AuthUser,
    QuartAuth,
    Unauthorized,
)
import secrets
from aioprometheus import Summary, Gauge, Registry, render, inprogress, timer
import asyncio
import random

app = Quart(__name__)
QuartAuth(app=app)
app.secret_key = secrets.token_urlsafe(16)
BASE_DIR = os.getcwd()
app.template_folder = BASE_DIR + "/templates"

"REDDIT AUTHS"
app.config["client_secret"] = "_PbSwY4EnnwyrWkjn0zT7F3HLus_ig"
app.config["client_id"] = "5Y6sMsPxq94zxBzyWP-87A"
reddit_redirect_uri = "http://localhost:5000/reddit/callback"

"GAUGES AND SUMMARIES"
app.registry = Registry()
app.api_requests_gauge = Gauge(
    "quart_acive_requests", "number_of_active_requests_per_endpoint"
)
app.api_request_timer = Summary(
    "requests_processed_per_seconds", "Avg time spent processing request"
)
app.registry.register(app.api_requests_gauge)
app.registry.register(app.api_request_timer)


@app.route("/metrics")
async def handle_metrics():
    return render(app.registry, request.headers.getlist("accept"))


@app.route("/test_route1")
@timer(app.api_request_timer, labels={"path": "/test_route1"})
@inprogress(app.api_requests_gauge, labels={"path": "/test_route1"})
async def test_route1():
    asyncio.sleep(1.0)
    return "index"


@app.route("/test_route2")
@timer(app.api_request_timer, labels={"path": "/test_route2"})
@inprogress(app.api_requests_gauge, labels={"path": "/test_route2"})
async def test_route2():
    asyncio.sleep(random.randint(1000, 1500) / 1000.0)
    return "endpoint 2"


@app.before_serving
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        async with user_dal() as ud:
            await ud.create_user(
                name="peter", email="peter@gg.com", reddit_token_id="xx"
            )


def _reddit_oauth_url():
    scopes = [
        "submit",
        "flair",
        "history",
        "read",
        "subscribe",
        "privatemessages",
        "mysubreddits",
        "edit",
        "vote",
        "account",
        "modconfig",
        "modposts",
        "identity",
    ]
    state = "Mgj2XgDcGEnN1zfFDh7xtHQia8ZD8NaoAF"
    url = f"https://www.reddit.com/api/v1/authorize?client_id={app.config['client_id']}&response_type=code&state={state}&redirect_uri={reddit_redirect_uri}&duration=permanent&scope={','.join(scopes)}"
    return url


@app.before_request
def add_state():
    "This is required for the forms am using"
    request.state = ""


@app.route("/")
async def base_welcome():
    url = _reddit_oauth_url()
    return await render_template("welcome.html", reddit_auth=url)


@app.route("/home")
@login_required
async def home_page():
    return await render_template("logged_in.html")


@app.route("/reddit/callback")
async def reddit_call_back():
    code = request.args.get("code")
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": reddit_redirect_uri,
    }
    headers = {"User-Agent": "Jeeves-0.1"}
    auth = BasicAuth(app.config["client_id"], app.config["client_secret"])
    token_url = "https://www.reddit.com/api/v1/access_token"
    about_url = "https://oauth.reddit.com/api/v1/me"

    async with aiohttp.ClientSession() as session:
        async with session.post(
            token_url, auth=auth, data=data, headers=headers
        ) as resp:
            data = await resp.json()

        if "access_token" in data:
            access_token = data["access_token"]
            headers["Authorization"] = f"Bearer {access_token}"
            async with session.get(about_url, headers=headers) as about_response:
                data = await about_response.json()
                username = data["name"]

            async with user_dal() as ud:
                db_resp = await ud.get_user_by_name(username)
                if db_resp["Users"] == None:
                    db_resp = await ud.create_user(
                        name=username, email=None, reddit_token_id=access_token
                    )

                login_user(AuthUser(db_resp["id"]))
                return redirect(url_for("home_page"))

    return redirect(url_for("base_welcome"))


@app.route("/users")
async def get_all_users():
    async with user_dal() as ud:
        return await ud.get_all_users()


@app.route("/users/<int:user_id>")
async def get_user(user_id):
    async with user_dal() as ud:
        user = await ud.get_user(user_id=user_id)
        return user


@app.route("/create_user", methods=["GET", "POST"])
async def create_user():
    form = await UserForm.from_formdata(request=request)
    print(form.name)
    if request.method == "POST" and await form.validate():
        async with user_dal() as ud:
            await ud.create_user(
                form.name.data, form.email.data, form.reddit_token_id.data
            )
            return redirect("/users")

    return await render_template("create_user.html", form=form)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
