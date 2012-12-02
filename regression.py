from article import *

def basic_features(article, options):
  # Only uses basic features which can be pulled directly from the JSON data
  return [article.body_length(), article.percent_anonymous_edits()] + \
         [article.percent_top_edits()]

def token_features(article, options):
  # Takes into account the number of tokens in headings and body text
  vector = []
  heading_tokens = options['heading_tokens']
  body_tokens = options['body_tokens']
  for token in heading_tokens: vector.append(article.heading_tokens().count(token))
  for token in body_tokens: vector.append(article.body_text_tokens().count(token))
  return vector

def link_features(article, options):
  # Takes into the total number of edits of articles it links to and the average
  # number of edits than an article links to
  vector = []
  articles = options['articles']
  titles = [a.title() for a in articles]
  links_num_edits = [] # Number of edits of the articles that article links to
  for link in article.links():
    if link in titles:
      article = articles[titles.index(link)]
      links_num_edits.append(article.num_edits())
  vector.append(sum(links_num_edits))
  if sum(links_num_edits) > 0:
    vector.append(float(sum(links_num_edits)) / len(links_num_edits))
  else:
    vector.append(0)
  return vector

def generate_data(filepaths):
  articles = [Article(f) for f in filepaths]
  top_editors = []
  heading_tokens = []
  body_tokens = []
  for article in articles:
    for editor in article.top_editors():
      if editor not in top_editors: top_editors.append(editor)
    for token in article.heading_tokens():
      if token not in heading_tokens: heading_tokens.append(token)
    for token in article.body_text_tokens():
      if token not in body_tokens: body_tokens.append(token)
  options = {'articles': articles, 'top_editors': top_editors, 'heading_tokens': heading_tokens,\
             'body_tokens': body_tokens}
  data = []
  for a in articles:
    feature_vector = basic_features(article, options) + token_features(article, options) + \
                     link_features(article, options)
    data.append((feature_vector, a.num_edits()))
  return data

#def train(data, loss_fn, gradient_fn, num_rounds = 100, step_size = 0.5, regularization = 0):
  # data is a list of (feature_vector, num_edits) tuples, where feature_vector is a list
  # This function returns trained weights using stochastic gradient descent
  #TODO: finish
  #num_features = len(data[0][0])
  #weights = [0 for i in range(num_features)]
  #for i in range(num_rounds):


# Below is just a test
print generate_data(['Elephant.json'])
