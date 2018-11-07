import datetime
from flask import Flask, render_template, request
from pandas_datareader import data
from bokeh.plotting import figure, show, output_file, save
from bokeh.embed import components
from bokeh.resources import CDN

app = Flask(__name__)

@app.route('/')
def plot():

    global caption_elements
    caption_elements = []

    start = datetime.datetime.now() - datetime.timedelta(weeks=4)
    end = datetime.datetime.now()

    df = data.DataReader(name='NWS', data_source='yahoo', start=start, end=end)

    def inc_dec(o, c):
        if c > o:
            value = "Increase"
        elif c < o:
            value = "Decrease"
        else:
            value = "Equal"
        return value

    df["Status"]=[inc_dec(o,c) for o, c in zip(df.Open, df.Close)]
    df["Middle"]=(df.Open+df.Close)/2
    df["Height"]=abs(df.Close-df.Open)

    p=figure(x_axis_type='datetime', width=1000, height=300, title="Newscorp Stock")
    p.grid.grid_line_alpha=0.3

    hours_12=12*60*60*1000 # converts 12 hours to milliseconds

    p.segment(df.index, df.High, df.index, df.Low, color="black")

    p.rect(df.index[df.Status=="Increase"], df.Middle[df.Status=="Increase"],
           hours_12, df.Height[df.Status=="Increase"], fill_color="#CCFFFF", line_color="black")

    p.rect(df.index[df.Status=="Decrease"], df.Middle[df.Status=="Decrease"],
           hours_12, df.Height[df.Status=="Decrease"], fill_color="#FF3333", line_color="black")

    up = 0
    down = 0

    for item in list(df.loc[:,"Status"]):
        if item == "Increase":
            up += 1
        elif item == "Decrease":
            down += 1

    if up > down:
        caption_elements=['up', 'happy', "../static/images/happyrupert.jpg"]
    elif down > up:
        caption_elements=['down', 'sad', "../static/images/sadrupert.jpg"]
    elif down > up:
        caption_elements=['equal', 'ambivalent', "../static/images/ambivalentrupert.jpg"]

    #Generates a tuple with javascript and html source code assigns the two elements to variables
    script1, div1 = components(p)

    #Content Delivery Network keeps js and css up to date
    cdn_js=CDN.js_files[0]
    cdn_css=CDN.css_files[0]

    return render_template("MMI.html",
    script1=script1,
    div1=div1,
    cdn_css=cdn_css,
    cdn_js=cdn_js,
    caption_elements=caption_elements)

if __name__=="__main__":
    app.run(debug=True, use_reloader=False)
