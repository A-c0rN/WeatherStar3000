# Retro Winnipeg Weather Channel
# By probnot
# V0.0.17

# Standard Library
import ssl
import time
from datetime import datetime
from math import log
from tkinter import *

# Third-Party
import feedparser
from geopy.geocoders import Nominatim
from metar.Metar import Metar
from meteostat import Daily, Hourly, Point
from requests import get

if hasattr(ssl, "_create_unverified_context"):
    ssl._create_default_https_context = ssl._create_unverified_context

geolocator = Nominatim(user_agent="myapplication")

location = geolocator.geocode("Milwaukee, WI")
lat = float(location.raw["lat"])
lon = float(location.raw["lon"])

print(lat, lon)

clockShown = False
weatherShown = False
scrollShown = False
status = 0
style = 0


def degrees_to_cardinal(d, small: bool = False):
    """
    note: this is highly approximate...
    """
    dirs = [
        "N",
        "NNE",
        "NE",
        "ENE",
        "E",
        "ESE",
        "SE",
        "SSE",
        "S",
        "SSW",
        "SW",
        "WSW",
        "W",
        "WNW",
        "NW",
        "NNW",
    ]
    if small:
        dirs = [
            "N",
            "NE",
            "E",
            "SE",
            "S",
            "SW",
            "W",
            "NW",
        ]
    ix = round(d / (360.0 / len(dirs)))
    return dirs[ix % len(dirs)]


table = {
    "1": "Clear",
    "2": "Fair",
    "3": "Cloudy",
    "4": "Overcast",
    "5": "Fog",
    "6": "Freezing Fog",
    "7": "Light Rain",
    "8": "Rain",
    "9": "Heavy Rain",
    "10": "Freezing Rain",
    "11": "Heavy Freezing Rain",
    "12": "Sleet",
    "13": "Heavy Sleet",
    "14": "Light Snowfall",
    "15": "Snowfall",
    "16": "Heavy Snowfall",
    "17": "Rain Shower",
    "18": "Heavy Rain Shower",
    "19": "Sleet Shower",
    "20": "Heavy Sleet Shower",
    "21": "Snow Shower",
    "22": "Heavy Snow Shower",
    "23": "Lightning",
    "24": "Hail",
    "25": "Thunderstorm",
    "26": "Heavy Thunderstorm",
    "27": "Storm",
}


def clock():
    current = datetime.now()
    day = str(current.day).rjust(2, " ")
    hour = str(int(current.strftime("%I"))).rjust(2, " ")
    if clockShown and not scrollShown:
        marquee.itemconfigure(
            timeMQ,
            text=datetime.now()
            .strftime(f"%a %b {day}           {hour}:%M:%S %p")
            .upper(),
        )
        marquee.itemconfigure(
            timeMQ2,
            text=datetime.now()
            .strftime(f"%a %b {day}           {hour}:%M:%S %p")
            .upper(),
        )
    else:
        marquee.itemconfigure(timeMQ, text="")
        marquee.itemconfigure(timeMQ2, text="")
    marquee.update()
    root.after(1000, clock)  # run every 1sec


def scroll():
    global status
    if scrollShown and not clockShown:
        marquee.itemconfigure(text, font=("Star3", 38))
        marquee.itemconfigure(text2, font=("Star3 Outline", 38))
        restart_marquee = True  #
        while restart_marquee:
            restart_marquee = False
            for p in range(pixels + 601):
                marquee.move(
                    text, -1, 0
                )  # shift the canvas to the left by 1 pixel
                marquee.move(
                    text2, -1, 0
                )  # shift the canvas to the left by 1 pixel
                if not scrollShown:
                    break
                marquee.update()
                time.sleep(0.005)  # scroll every 5ms
                if p == pixels + 600:  # once the canvas has finished scrolling
                    restart_marquee = True
                    marquee.move(text, pixels + 600, 0)  # reset the location
                    marquee.move(text2, pixels + 600, 0)  # reset the location
                    p = 0  # keep the for loop from ending
            if not scrollShown:
                break
    elif weatherShown and not scrollShown:
        DTNow = datetime.now()
        hour = datetime.fromtimestamp(DTNow.timestamp() - 3600)
        month = datetime(DTNow.year, DTNow.month, 1, 0, 0, 0, 0)
        now = (
            Hourly(
                Point(lat, lon),
                start=hour,
                end=DTNow,
            )
            .fetch()
            .values.tolist()[-1]
        )
        hist = (
            Daily(
                Point(lat, lon),
                start=month,
                end=DTNow,
            )
            .fetch()
            .values.tolist()
        )
        monthlyPrecip = 0.0
        for i in hist:
            monthlyPrecip += i[3]
        oof = Metar(
            get(
                "https://tgftp.nws.noaa.gov/data/observations/metar/stations/KMWC.TXT"
            )
            .content.decode("utf-8")
            .split("\n")[1]
        )
        cond = table[str(int(now[-1]))].upper()
        temp = str(int(round((now[0] * (9 / 5)) + 32, 0))).rjust(3, " ")
        humid = str(int(now[2])).rjust(3, " ")
        dewpt = str(int(round((now[1] * (9 / 5)) + 32, 0))).rjust(3, " ")
        press = round(0.0295300 * now[8], 2)
        wind = (
            f'{oof.wind("MPH").upper().split(" AT ")[0]} {oof.wind("MPH").upper().split(" AT ")[1].split(",")[0].rjust(6, " ")}'
            if oof.wind("MPH") != "calm"
            else "CALM"
        )
        vis = str(oof.vis).replace("miles", "MI.").rjust(6, " ")
        celing = (
            (str(oof.sky[0][1]).replace("feet", "FT.").rjust(9, " "))
            if oof.sky[0][0] != "CLR"
            else "UNLIMITED"
        )
        monthlyPrecip = (
            str(round(monthlyPrecip, 2)).ljust(5, "0")
            if monthlyPrecip >= 10
            else str(round(monthlyPrecip, 2)).zfill(4, "0")
        )
        marquee.itemconfigure(text, font=("Star3", 29))
        marquee.itemconfigure(text2, font=("Star3 Outline", 29))
        if status == 0:
            marquee.itemconfigure(text, text="CONDITIONS AT MILWAUKEE")
            marquee.itemconfigure(text2, text="CONDITIONS AT MILWAUKEE")
            status += 1
        elif status == 1:
            marquee.itemconfigure(text, text=cond)
            marquee.itemconfigure(text2, text=cond)
            status += 1
        elif status == 2:
            marquee.itemconfigure(text, text=f"TEMP: {temp}°F")
            marquee.itemconfigure(text2, text=f"TEMP: {temp}°F")
            status += 1
        elif status == 3:
            marquee.itemconfigure(
                text, text=f"HUMIDITY: {humid}%   DEWPOINT:{dewpt}°F"
            )
            marquee.itemconfigure(
                text2, text=f"HUMIDITY: {humid}%   DEWPOINT:{dewpt}°F"
            )
            status += 1
        elif status == 4:
            marquee.itemconfigure(
                text, text=f"BAROMETRIC PRESSURE: {press} IN."
            )
            marquee.itemconfigure(
                text2, text=f"BAROMETRIC PRESSURE: {press} IN."
            )
            status += 1
        elif status == 5:
            marquee.itemconfigure(text, text=f"WIND: {wind}")
            marquee.itemconfigure(text2, text=f"WIND: {wind}")
            status += 1
        elif status == 6:
            marquee.itemconfigure(text, text=f"VISIB:  {vis} CEILING:{celing}")
            marquee.itemconfigure(
                text2, text=f"VISIB:  {vis} CEILING:{celing}"
            )
            status += 1
        elif status == 7:
            marquee.itemconfigure(
                text,
                text=f"{DTNow.strftime('%B').upper()} PRECIPITATION: {monthlyPrecip} IN.",
            )
            marquee.itemconfigure(
                text2,
                text=f"{DTNow.strftime('%B').upper()} PRECIPITATION: {monthlyPrecip} IN.",
            )
            status = 0
        marquee.update()
    else:
        marquee.itemconfigure(text, text="")
        marquee.itemconfigure(text2, text="")
        marquee.update()
    root.after(4500, scroll)  # run every 1sec


def genText(
    obj: Canvas,
    font: str,
    msg: str,
    x: int,
    y: int,
    size: int,
    overflow: bool = False,
):
    ovfl = 0 if not overflow else 540
    text2 = obj.create_text(
        x,
        y,
        anchor="nw",
        text=msg,
        font=(
            font + " Outline",
            size,
        ),
        fill="black",
        width=ovfl,
    )

    text = obj.create_text(
        x,
        y,
        anchor="nw",
        text=msg,
        font=(
            font,
            size,
        ),
        fill="white",
        width=ovfl,
    )
    return text, text2


def genPage(top: Canvas):
    global style
    if style == 0:
        DTNow = datetime.now()
        hour = datetime.fromtimestamp(DTNow.timestamp() - 3600)
        month = datetime(DTNow.year, DTNow.month, 1, 0, 0, 0, 0)
        now = (
            Hourly(
                Point(lat, lon),
                start=hour,
                end=DTNow,
            )
            .fetch()
            .values.tolist()[-1]
        )
        hist = (
            Daily(
                Point(lat, lon),
                start=month,
                end=DTNow,
            )
            .fetch()
            .values.tolist()
        )
        monthlyPrecip = 0.0
        for i in hist:
            monthlyPrecip += i[3]
        oof = Metar(
            get(
                "https://tgftp.nws.noaa.gov/data/observations/metar/stations/KMWC.TXT"
            )
            .content.decode("utf-8")
            .split("\n")[1]
        )
        cond = table[str(int(now[-1]))].upper()
        temp = str(int(round((now[0] * (9 / 5)) + 32, 0))).rjust(3, " ")
        humid = str(int(now[2])).rjust(3, " ")
        dewpt = str(int(round((now[1] * (9 / 5)) + 32, 0))).rjust(3, " ")
        press = round(0.0295300 * now[8], 2)
        wind = (
            f'{oof.wind("MPH").upper().split(" AT ")[0]} {oof.wind("MPH").upper().split(" AT ")[1].rjust(6, " ")}'
            if oof.wind("MPH") != "calm"
            else "CALM"
        )
        vis = str(oof.vis).replace("miles", "MI.").rjust(6, " ")
        celing = (
            (str(oof.sky[0][1]).replace("feet", "FT.").rjust(9, " "))
            if oof.sky[0][0] != "CLR"
            else "UNLIMITED"
        )
        monthlyPrecip = (
            str(round(monthlyPrecip, 2)).ljust(5, "0")
            if monthlyPrecip >= 10
            else str(round(monthlyPrecip, 2)).zfill(4, "0")
        )
        s1, s1b = genText(
            top, "Star3", "CONDITIONS AT MILWAUKEE", 66, 50 + (39 * 0), 29
        )
        s2, s2b = genText(top, "Star3", cond, 66, 50 + (39 * 1), 29)
        s3, s3b = genText(
            top, "Star3", f"TEMP: {temp}°F", 66, 50 + (39 * 2), 29
        )
        s4, s4b = genText(
            top,
            "Star3",
            f"HUMIDITY: {humid}%   DEWPOINT:{dewpt}°F",
            66,
            50 + (39 * 3),
            29,
        )
        s5, s5b = genText(
            top,
            "Star3",
            f"BAROMETRIC PRESSURE: {press} IN.",
            66,
            50 + (39 * 4),
            29,
        )
        s6, s6b = genText(
            top,
            "Star3",
            f"WIND: {wind}",
            66,
            50 + (39 * 5),
            29,
        )
        s7, s7b = genText(
            top,
            "Star3",
            f"VISIB:  {vis} CEILING:{celing}",
            66,
            50 + (39 * 6),
            29,
        )
        s8, s8b = genText(
            top,
            "Star3",
            f"{DTNow.strftime('%B').upper()} PRECIPITATION: {monthlyPrecip} IN.",
            66,
            50 + (39 * 7),
            29,
        )
        s9, s9b = genText(
            top,
            "Star3",
            "",
            66,
            50 + (39 * 7),
            29,
        )
        style += 1
    elif style == 1:
        s1, s1b = genText(
            top,
            "Star3",
            "   LATEST HOURLY OBSERVATIONS   ",
            66,
            50 + (39 * 0),
            29,
        )
        s2, s2b = genText(
            top,
            "Star3 Small",
            "LOCATION       °F WEATHER   WIND",
            66,
            32 + (39 * 1),
            29,
        )
        s3, s3b = genText(
            top,
            "Star3",
            f"CHICAGO INTL  000 WXwxWXwx  WIwi",
            66,
            32 + (39 * 2),
            29,
        )
        s4, s4b = genText(
            top,
            "Star3",
            f"MILWAUKEE     000 WXwxWXwx  WIwi",
            66,
            32 + (39 * 3),
            29,
        )
        s5, s5b = genText(
            top,
            "Star3",
            f"WAUKESHA      000 WXwxWXwx  WIwi",
            66,
            32 + (39 * 4),
            29,
        )
        s6, s6b = genText(
            top,
            "Star3",
            f"KENOSHA       000 WXwxWXwx  WIwi",
            66,
            32 + (39 * 5),
            29,
        )
        s7, s7b = genText(
            top,
            "Star3",
            f"MADISON       000 WXwxWXwx  WIwi",
            66,
            32 + (39 * 6),
            29,
        )
        s8, s8b = genText(
            top,
            "Star3",
            f"GREEN BAY     000 WXwxWXwx  WIwi",
            66,
            32 + (39 * 7),
            29,
        )
        s9, s9b = genText(
            top,
            "Star3",
            f"GRAND RAPIDS  000 WXwxWXwx  WIwi",
            66,
            32 + (39 * 8),
            29,
        )
        style = 0


oof = False


def weather_page():
    global oof
    global clockShown
    global scrollShown
    global weatherShown
    clockShown = False
    weatherShown = True
    bg = "green"
    top = Canvas(root, width=640, height=385, bg=bg, highlightthickness=0)
    top.place(x=0, y=0)
    if oof:
        bg = "blue"
        top.config(bg=bg)
        genPage(top)

        if not scrollShown:
            clockShown = True
            weatherShown = True
    oof = True
    root.after(14000, weather_page)
    # no_desc = genText(page, "Star3", "TEST", 0, 0, 25, True)


root = Tk()
root.attributes("-fullscreen", False)
root.geometry("640x480")
root.minsize(640, 480)
root.maxsize(640, 480)
root.config(cursor="none", bg="blue")
root.wm_title("wpg-weatherchan_V0.0.17")

weather_page()

marquee = Canvas(root, height=70, width=510, bg="blue", highlightthickness=0)
marquee.place(x=66, y=387)

sep = Canvas(root, height=2, width=640, bg="white", highlightthickness=0)
sep.place(x=0, y=385)

url = "https://winnipeg.ca/interhom/RSS/RSSNewsTopTen.xml"
wpg = feedparser.parse(url)

# use the first 8 entries on the wpg news RSS feed
mrq_msg = f'{" "*29}{wpg.entries[0]["description"]}{" "*29}{wpg.entries[1]["description"]}{" "*29}{wpg.entries[2]["description"]}{" "*29}{wpg.entries[3]["description"]}{" "*29}{wpg.entries[4]["description"]}{" "*29}{wpg.entries[5]["description"]}{" "*29}{wpg.entries[6]["description"]}{" "*29}{wpg.entries[7]["description"]}{" "*29}'.upper()

# use the length of the news feeds to determine the total pixels in the scrolling section
marquee_length = len(mrq_msg)
if (marquee_length * 45) < 31000:
    pixels = marquee_length * 45  # roughly 24px per char
else:
    pixels = 31000

# setup scrolling text

text, text2 = genText(marquee, "Star3", mrq_msg, 1, 20, 38)

timeMQ, timeMQ2 = genText(
    marquee,
    "Star3 Small",
    datetime.now().strftime("%a %b %d           %I:%M:%S %p").upper(),
    1,
    -16,
    29,
)

clock()
scroll()
root.mainloop()
