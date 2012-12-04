import json
from article import *
import random
from parser import DELIMITER
import math

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
  articles = read_articles(filepath)

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
    feature_vector = [1] + basic_features(article, options) + token_features(article, options) + \
                     link_features(article, options) # The [1] is a constant factor
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

def vector_abs(list1):
  # Takes the absolute value of a list
  return [abs(elem) for elem in list1]

def logistic_gradient(features, target, weights): 
  dot = dot_product(weights, features)
  denom = 1 + math.exp(-1 * dot * target)
  coeff = target * (-1 + (1 / denom))
  return scalar_product(features, coeff)

def squared_gradient(features, target, weights):
  margin = dot_product(weights, features) - target
  return scalar_product(features, margin)

def read_articles(filepath):
  """ Given the path to a file containing JSON for article data, return a list
  of Articles for that data. """
  file = open(filepath)
  lines = file.readlines()
  articles = []
  json_string = ""
  articles_appended = 0
  for line in lines:
    if line.strip() == DELIMITER.strip():
      print(json_string)
      articles.append(Article(json_string))
      articles_appended += 1
      json_string = ""
    else:
      json_string += line
  if len(json_string) > 0: articles.append(Article(json_string)) # Get last article
  file.close()
  return articles

def train(data, gradient_fn, num_rounds = 100, init_step_size = 0.01, step_size_reduction = 0.1, regularization_factor = 0.001):
  # data is a list of (feature_vector, num_edits) tuples, where feature_vector is a list
  # step_size should be greater than 0; step_size_reduction is in [0, 1]
  # This function returns trained weights using stochastic gradient descent
  num_features = len(data[0][0])
  weights = [0.0 for i in range(num_features)]
  for i in range(num_rounds):
    random.shuffle(data)
    for j in range(len(data)):
      d = data[j]
      step_size = init_step_size / float((j + 1) ** step_size_reduction)
      feature_vector = d[0]
      num_edits = d[1]
      update = scalar_product(gradient_fn(feature_vector, num_edits, weights), -1 * step_size)
      regularization = scalar_product(weights, -1 * float(regularization_factor) / len(data))
      weights = vector_sum(weights, vector_sum(update, regularization))
  return weights

def predict(weights, features):
  return dot_product(weights, features)

if __name__ == "__main__":
   random.seed(42)
   #data = [([1,2],2), ([1,3],3), ([10,9],9)]
   #weights = train(data, logistic_gradient, 100000)
   data = generate_data('train.json')
   weights = train(data, squared_gradient)
   print 'WEIGHTS'
   print weights
   """for d in data:
     print predict(weights, d[0]), d[1]"""
