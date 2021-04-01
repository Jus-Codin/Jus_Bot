import flask, os, wolframalpha, wikipedia
from urllib.parse import unquote
from threading import Thread

def run():
  print(__file__)
  app=flask.Flask('', template_folder=__file__.replace('__init__.py', 'templates'))
  client=wolframalpha.Client(os.getenv("APPID"))

  def removeBrackets(variable):
    return variable.split('(')[0]

  def resolveListOrDict(variable):
    if isinstance(variable, list):
      return variable[0]['plaintext']
    else:
      return variable['plaintext']

  def outputter(text=""):
    return flask.render_template("index.html", output=flask.escape(text))

  @app.route('/') 
  def home():
      return outputter("I'm alive")

  @app.route('/google/<path:keyword>')
  def google(keyword):
    return flask.redirect(f'https://www.google.com/search?q={keyword}')

  @app.route("/wiki_search/<path:keyword>")
  def search_wiki(keyword):
    searchResults = wikipedia.search(unquote(keyword))
    # If there is no result, print no result
    if not searchResults:
      return outputter("No result from Wikipedia")
    try:
      page = wikipedia.page(searchResults[0])
    except wikipedia.exceptions.DisambiguationError as err:
      # Select the first item in the list
      page = keyword + ' can refer to:\n' + '\n'.join(err.options)
      return outputter(page)
    wikiSummary = str(page.summary.encode('utf-8'))[2:-1].encode('latin1').decode('unicode-escape').encode('latin1').decode('utf-8')
    return outputter(wikiSummary)

  @app.route("/wolfram/<path:text>")
  def wolfram_search(text):
    res = client.query(unquote(text))
    if res['@success'] == 'false':
      return outputter('Question cannot be resolved')
    else:
      result = ''
      pod0 = res['pod'][0]
      pod1 = res['pod'][1]
      # checking if pod1 has primary=true or title=result|definition
      if (('definition' in pod1['@title'].lower()) or ('result' in  pod1['@title'].lower()) or (pod1.get('@primary','false') == 'true')):
        # extracting result from pod1
        result = resolveListOrDict(pod1['subpod'])
        return outputter(result)
      else:
        # extracting wolfram question interpretation from pod0
        question = resolveListOrDict(pod0['subpod'])
        # removing unnecessary parenthesis
        question = removeBrackets(question)
        # searching for response from wikipedia
        return search_wiki(question)

  @app.route('/ip')
  def get_ip():
    return outputter(flask.request.environ['HTTP_X_FORWARDED_FOR'])

  @app.route('/code')
  def show_code():
    return """<iframe height="100%" width="100%" src="https://replit.com/@JusCodin/Discord-Bot-Mk3?lite=true" scrolling="no" frameborder="no" allowtransparency="true" allowfullscreen="true" sandbox="allow-forms allow-pointer-lock allow-popups allow-same-origin allow-scripts allow-modals"></iframe>"""

  @app.route('/<path:unknown>')
  def unknown_command(unknown):
    return outputter(f'Unknown command "{unquote(unknown)}"')

  app.run("0.0.0.0",8080)

def open_web():
  t = Thread(target=run)
  t.start()
