import json
from article import *
import random
from parser import DELIMITER
import math
import operator

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

def expand_features(features):
  # The features and the features squared
  new_features = []
  for i in range(len(features)):
    new_features.append(features[i] * features[i])
  return features + new_features


def generate_data(train_filepath, test_filepath, expandFeatures):
  # First it loads the article from JSON objects in filepath
  # Then it creates the X (feature vector) and Y (num_edits) tuples for each article
  train_articles = read_articles(train_filepath)
  test_articles = read_articles(test_filepath)
  all_articles = train_articles + test_articles

  top_editors = []
  heading_tokens = []
  body_tokens = []
  for article in all_articles:
    for editor in article.top_editors():
      if editor not in top_editors: top_editors.append(editor)
    for token in article.heading_tokens():
      if token not in heading_tokens: heading_tokens.append(token)
    # for token in article.body_text_tokens():
      # if token not in body_tokens: body_tokens.append(token)
  options = {'articles': all_articles, 'top_editors': top_editors, 'heading_tokens': heading_tokens}#, \
             # 'body_tokens': body_tokens}
  train_data = []
  test_data = []

  for article in train_articles:
    feature_vector = basic_features(article, options) + token_features(article, options) + \
                     link_features(article, options)
    if expandFeatures:
      feature_vector = [1] + expand_features(feature_vector)
    else:
      feature_vector = [1] + feature_vector
    train_data.append((feature_vector, article.num_edits()))

  for article in test_articles:
    feature_vector = basic_features(article, options) + token_features(article, options) + \
                     link_features(article, options)
    if expandFeatures:
      feature_vector = [1] + expand_features(feature_vector)
    else:
      feature_vector = [1] + feature_vector
    test_data.append((feature_vector, article.num_edits()))

  return (train_data, test_data)

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

def squared_loss(features, target, weights):
  margin = dot_product(weights, features) - target
  return 0.5 * margin ** 2


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
      # TODO: Get rid of outliers
      article = Article(json_string)
      if article.num_edits() < 20: # Outliers
        json_string = ""
        continue
      articles.append(article)
      articles_appended += 1
      json_string = ""
      if articles_appended > 50: break # TODO: shorten testing
    else:
      json_string += line
  if len(json_string) > 0: articles.append(Article(json_string)) # Get last article
  file.close()
  return articles


def train(data, gradient_fn, loss_fn, num_rounds = 1200, init_step_size = 9e-22, step_size_reduction = 1e-30, regularization_factor = 10):
  # squared_loss: num_rounds = 500, init_step_size = 1e-14, step_size_reduction = 1e-15, regularization_factor = 1e-3
  # logistic_loss: num_rounds = 500, init_step_size = 5e-10, step_size_reduction = 1e-10, regularization_factor = 1e-3
  # data is a list of (feature_vector, num_edits) tuples, where feature_vector is a list
  # step_size should be greater than 0; step_size_reduction is in [0, 1]
  # This function returns trained weights using stochastic gradient descent
  num_features = len(data[0][0])
  weights = [0.0 for i in range(num_features)]
  for i in range(num_rounds):
    if i % 100 == 0: print "Starting Round " + str(i + 1)
    random.shuffle(data)
    for j in range(len(data)):
      d = data[j]
      step_size = init_step_size / float((j + 1) ** step_size_reduction)
      feature_vector = d[0]
      num_edits = d[1]
      update = scalar_product(gradient_fn(feature_vector, num_edits, weights), -1 * step_size)
      regularization = scalar_product(weights, -1 * float(regularization_factor) / len(data))
      weights = vector_sum(weights, vector_sum(update, regularization))
    if i % 100 == 0:
      loss = 0
      for d in data:
        loss += loss_fn(d[0], d[1], weights)
      print loss
  return weights

def predict(weights, features):
  return dot_product(weights, features)

def test(data, weights, loss_fn, verbose = False):
  # data is a list of (feature_vector, num_edits) tuples, where feature_vector is a list
  loss_total = 0
  identifier = 0
  percent_losses = []
  tuples = []
  for d in data:
    feature_vector = d[0]
    target = d[1]
    prediction = predict(weights, feature_vector)
    tuples.append((identifier, target, prediction)) # append 3-tuple to list for rankings

    loss = loss_fn(feature_vector, target, weights)
    percent_loss = round(100 * float(target - prediction) / target, 2)
    percent_losses.append(percent_loss)
    loss_total += loss
    if verbose: print "Prediction: " + str(prediction) + "; Target: " + str(target) + \
                      "; Loss: " + str(loss) + "; Error: " + str(percent_loss) + "%"
    identifier += 1
  if verbose:
    percent_losses = vector_abs(percent_losses) # To correctly calculate avg and max
    print "\nTotal Loss: " + str(loss_total)
    print "Average Error: " + str(sum(percent_losses) / len(percent_losses)) + "%"
    print "Max Error: " + str(max(percent_losses)) + "%"

    ranked_targets = rank(tuples, 1)
    ranked_predictions = rank(tuples, 2)
    
    target_pairs = get_pairs(ranked_targets)
    prediction_pairs = get_pairs(ranked_predictions)

    intersect = target_pairs.intersection(prediction_pairs)
    score = (float(len(intersect)) / len(target_pairs)) * 100

    print "Ranking score: " + str(score) + "%"

  return loss_total

def get_pairs(data): 
  # run on ranked array - only consider the 0th element of tuple
  pairs = set()
  for i in range(len(data)): 
    for j in range(i+1, len(data)): 
      pairs.add((data[i][0], data[j][0]))
  return pairs

def order(data): 
  ordered = []
  i = 0
  for pt in data: 
    ordered.append((i, pt[1]))
    i += 1
  return ordered


def rank(data, item): 
  ranked = sorted(data, key=operator.itemgetter(item))
  return ranked


# Below is just a test
if __name__ == "__main__":
  #TODO: train and test data token features => same length.....?
  random.seed(42)

  print "Generating data for least squares..."
  all_data = generate_data('train.json', 'test.json', False)
  train_data = all_data[0]
  test_data = all_data[1]

  print "Training the predictor..."
  weights = train(train_data, squared_gradient, squared_loss, num_rounds = 500,
    init_step_size = 1e-14, step_size_reduction = 1e-15, regularization_factor =
    1e-3)

  #print ''
  #print "weights: " + str(weights)
  #print ''
  #print "Testing the predictor..."
  test(test_data, weights, squared_loss, True)
  
  print "Generating data for least squares with basis expansion..."
  all_data = generate_data('train.json', 'test.json', True)
  train_data = all_data[0]
  test_data = all_data[1]


  print "Training the predictor..."
  weights = train(train_data, squared_gradient, squared_loss, num_rounds = 100,
    init_step_size = 9e-22, step_size_reduction = 0,
    regularization_factor = 7)
  test(test_data, weights, squared_loss, True)
  # step size 1e-30
  # step size 9e-22
  #
  # print weights
  # data = generate_data('WLion.json')
  # weights = train(data, squared_gradient)
  # print data
  # print ''
  # print weights
  # for d in data:
  #   print predict(weights, d[0]), d[1]
