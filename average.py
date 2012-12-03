import json
from article import *
from parser import DELIMITER
from regression import read_articles

def get_num_edits():
  """ Returns a list whose elements are the number of edits for each article in
  the training set. """
  articles = read_articles('test.json')
  # TODO Get number of edits from each article, average, implement fn to find
  # error on training and test sets.

get_num_edits()
