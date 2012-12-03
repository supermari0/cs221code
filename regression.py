import json
from article import *
from random import shuffle
from parser import DELIMITER

def basic_features(article, options):
  # Only uses basic features which can be pulled directly from the JSON data
  return [article.body_length(), article.percent_anonymous_edits()] + \
         [article.percent_top_edits()]

def token_features(article, options):
  # Takes into account the number of tokens in headings and body text
  vector = []
  heading_tokens = options['heading_tokens']
  # body_tokens = options['body_tokens']
  for token in heading_tokens: vector.append(article.heading_tokens().count(token))
  # for token in body_tokens: vector.append(article.body_text_tokens().count(token))
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

def generate_data(filepath):
  # First it loads the article from JSON objects in filepath
  # Then it creates the X (feature vector) and Y (num_edits) tuples for each article
  file = open(filepath)
  lines = file.readlines()
  articles = []
  json_string = ""
  for line in lines:
    if line.strip() == DELIMITER.strip():
      articles.append(Article(json_string))
      json_string = ""
    else:
      json_string += line
  if len(json_string) > 0: articles.append(Article(json_string)) # Get last article
  file.close()

  top_editors = []
  heading_tokens = []
  body_tokens = []
  for article in articles:
    for editor in article.top_editors():
      if editor not in top_editors: top_editors.append(editor)
    for token in article.heading_tokens():
      if token not in heading_tokens: heading_tokens.append(token)
    # for token in article.body_text_tokens():
      # if token not in body_tokens: body_tokens.append(token)
  options = {'articles': articles, 'top_editors': top_editors, 'heading_tokens': heading_tokens}#, \
             # 'body_tokens': body_tokens}
  data = []
  for article in articles:
    feature_vector = basic_features(article, options) + token_features(article, options) + \
                     link_features(article, options)
    data.append((feature_vector, article.num_edits()))
  return data

def dot_product(list1, list2):
  # Take the dot product of two lists of the same length
  if len(list1) != len(list2): raise Exception("list1 and list2 must have the same length")
  product = 0
  for i in range(len(list1)):
    product += list1[i] * list2[i]
  return product

def scalar_product(vector, scalar):
  # Multiply a list (vector) by a scalar to do scalar multiplication
  product = []
  for i in range(len(vector)):
    product.append(vector[i] * scalar)
  return product

def vector_sum(list1, list2):
  # Take the sum of two lists of the same length
  if len(list1) != len(list2): raise Exception("list1 and list2 must have the same length")
  return [list1[i] + list2[i] for i in range(len(list1))]


def squared_gradient(features, target, weights):
  margin = dot_product(weights, features) - target
  return scalar_product(features, margin)

def train(data, gradient_fn, num_rounds = 100, init_step_size = 1.0, regularization = 0):
  # data is a list of (feature_vector, num_edits) tuples, where feature_vector is a list
  # step_size should be greater than 0
  # This function returns trained weights using stochastic gradient descent
  num_features = len(data[0][0])
  weights = [0.0 for i in range(num_features)]
  for i in range(num_rounds):
    shuffle(data)
    step_size = init_step_size * 1 / float(i + 1)
    for d in data:
      feature_vector = d[0]
      num_edits = d[1]
      update = scalar_product(gradient_fn(feature_vector, num_edits, weights), -1 * step_size)
      weights = vector_sum(weights, update)
  return weights

# Below is just a test
if __name__ == "__main__":
  # data = generate_data('WLion.json')
  # weights = train(data, squared_gradient)
  # print data
  # print weights