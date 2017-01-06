import json
import httplib2

from apiclient import discovery
from oauth2client import client
from jinja2 import StrictUndefined
from flask import (Flask, jsonify, render_template, redirect, request, flash,
                    session, url_for, request)
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "TBD"

# Raise an error if you find an undefined variable in Jinja2
app.jinja_env.undefined = StrictUndefined
app.jinja_env.auto_reload = True

@app.route('/')
def index():
  if 'credentials' not in session:
    print "I don't have credentials, I'm redirecting to url_for Oauthcallback"
    return redirect(url_for('oauth2callback'))

  credentials = client.OAuth2Credentials.from_json(session['credentials'])

  if credentials.access_token_expired:
    print "I have credentials but the token has expired! redirect to url_for Oauthcallback"
    return redirect(url_for('oauth2callback'))

  else:
    http_auth = credentials.authorize(httplib2.Http())
    drive_service = discovery.build('drive', 'v2', http_auth)
    files = drive_service.files().list().execute()
    print "Json dumps"
    return json.dumps(files)


@app.route('/oauth2callback')
def oauth2callback():
  flow = client.flow_from_clientsecrets(
      'client_secret.json',
      scope='https://www.googleapis.com/auth/spreadsheets',
      redirect_uri="http://localhost:5000/oauth2callback")

  if 'code' not in request.args:
    auth_uri = flow.step1_get_authorize_url()
    print "Something something code in flow."
    return redirect(auth_uri)

  else:
    auth_code = request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    session['credentials'] = credentials.to_json()
    print "coming back to the url for index now. WEEEEE!"
    return redirect(url_for('index'))

if __name__ == "__main__":
    import uuid

    app.secret_key = str(uuid.uuid4())
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True

    # Use the DebugToolbar
    DebugToolbarExtension(app)
    
    app.run(host="0.0.0.0", port=5000)


