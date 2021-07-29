import requests
import codecs
from datetime import datetime 
import pytz

TZ_OFFSET = 'etc/gmt-1'

USE_STYLESHEET = True
STYLESHEET_URL = 'https://cdn.jsdelivr.net/npm/picnic@6.5.5/picnic.min.css'
# STYLESHEET_URL = 'https://unpkg.com/mvp.css'
# STYLESHEET_URL = 'https://cdn.jsdelivr.net/npm/water.css@2/out/water.css'

# Returns the calculated current hashflags URL, and an appropriate output filename
def currentHashFlagURL():
    global output_filename
    date_template = datetime.now(pytz.timezone(TZ_OFFSET)).isoformat()[0:13].replace('T','-');
    output_filename = 'config-%s.html' % date_template
    return 'https://pbs.twimg.com/hashflag/config-%s.json' % date_template, output_filename

# Returns a readable string format for the timestamp
def timestampToReadable(timestamp):
    try:
        return (datetime.fromtimestamp(int(round( timestamp / 1000)))).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return "???" # FIXME: Something is not right here, but it MOSTLY works, so whatever...

def getSorter(camp):
    return camp['campaignName']

#####################################################################
input_url, output_filename = currentHashFlagURL()

# If you try to access the current config within the first
# five or so minutes, it may not be available yet.
try:
    r = requests.get(input_url)
    campaigns = r.json()
except Exception as err:
    print("❌ Problem parsing %s (%s)" % (input_url, err))
    print("❌ The current hashflag config file may not be available yet; wait a few minutes.")
    exit(-1)

# Sort by the campaign name, by default
campaigns.sort(key=getSorter)

# Each `campaigns` entry contains:
# - campaignName        -- Campaign the hashflag belongs to (e.g. "BlackHistoryMonth")
# - hashtag             -- the actual hashtag to insert the image after (e.g. #bhm)
# - assetUrl            -- path to the icon image for the hashflag
# - startingTimestampMs -- presumably defines the range when the campaign is active
# - endingTimestampMs

out_buffer = ""

out_buffer += "<html><head><meta charset='UTF-8'>"

if USE_STYLESHEET:
    out_buffer += "<meta name='viewport' content='width=device-width, initial-scale=1'>"
    out_buffer += "<link rel='stylesheet' href='%s'>" % STYLESHEET_URL

out_buffer += "</head><body>"
              
out_buffer += "<div style='text-align:center'>"
out_buffer += "<a href='%s'>%s</a><br/>(%d entries)" % (input_url, input_url, len(campaigns))
out_buffer += "</div><br/>"
out_buffer += "<table style='max-width:1280px; margin:auto; display:table'>"

# TODO: Group by campaign name

for index, hash in enumerate(campaigns):
    out_buffer += "<tr>"
    out_buffer += "<td>%d</td>" % index
    out_buffer += "<td>%s</td>" % hash['campaignName']
    out_buffer += "<td><a href='https://twitter.com/search?src=typed_query&q=%%23%s'>#%s</a></td>" % (hash['hashtag'], hash['hashtag'])
    out_buffer += "<td style='font-family:monospace'><span style='color:green'>%s</span><br/><span style='color:red'>%s</span></td>" % (
            timestampToReadable(int(hash['startingTimestampMs'])), 
            timestampToReadable(int(hash['endingTimestampMs']))
        )
    out_buffer += "<td><a href='%s'><img src='%s'/></a></td>" % (hash['assetUrl'], hash['assetUrl'])
    out_buffer += "</tr>"

out_buffer += "</table></body></html>"

# Dump it out
outfile = codecs.open(output_filename, "w", "utf8")
outfile.write(out_buffer)
outfile.close()