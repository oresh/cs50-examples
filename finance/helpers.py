
from csv import reader
from urllib.request import urlopen
from urllib.error import HTTPError
from functools import wraps
from flask import redirect, render_template, request, session, url_for


def apology(top="", bottom=""):
    """Renders message as an apology to user."""
    def escape(url):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            url = url.replace(old, new)
        return url
    return render_template("apology.html", top=escape(top), bottom=escape(bottom))


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.11/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # reject symbol if it starts with caret
    if symbol.startswith("^"):
        return None

    # reject symbol if it contains comma
    if "," in symbol:
        return None

    # query Yahoo for quote
    # http://stackoverflow.com/a/21351911
    try:
        url = "http://download.finance.yahoo.com/d/quotes.csv?f=snl1&s={}".format(
            symbol)
        webpage = urlopen(url)
        datareader = reader(webpage.read().decode("utf-8").splitlines())
        row = next(datareader)
    except HTTPError:
        return None

    # ensure stock exists
    try:
        price = float(row[2])
    except FloatingPointError:
        return None

    # return stock's name (as a str), price (as a float), and (uppercased) symbol (as a str)
    return {
        "name": row[1],
        "price": price,
        "symbol": row[0].upper()
    }


def usd(value):
    """Formats value as USD."""
    return "${:,.2f}".format(value)
