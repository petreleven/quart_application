from starlette_wtf import StarletteForm
import wtforms as f
from wtforms.validators import DataRequired
from contextlib import asynccontextmanager


class UserForm(StarletteForm):
    name = f.StringField("name", [DataRequired("Please enter a name")])
    email = f.StringField("email", [DataRequired("Please enter an email")])
    reddit_token_id = f.StringField("Slack Id")
    # password = f.PasswordField("password")
    display = ["name", "email", "reddit_token_id"]


@asynccontextmanager
async def user_form():
    yield UserForm()
