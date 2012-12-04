import json
from article import *
from parser import DELIMITER
from regression import read_articles

def get_num_edits(filename):
  """ Returns a list whose elements are the number of edits for each article in
  the training set. """
  articles = read_articles(filename)
  # TODO Get number of edits from each article, average, implement fn to find
  # error on training and test sets.
  numEdits = [article.num_edits() for article in articles]
  return numEdits

def run_average_heuristic():
  numEditsTrain = get_num_edits('train.json') 
  averageNumEdits = sum(numEditsTrain) / float(len(numEditsTrain))
  numEditsTest = get_num_edits('test.json')

  differences = []
  for editCount in numEditsTest:
    difference = editCount - averageNumEdits
    differences.append(difference)

  totalDifference = sum(differences)
  averageDifference = sum(differences) / float(len(differences))

  print('Sum of differences between actual and predicted values: ' +
    str(totalDifference))
  print('Average difference between actual and predicted values: ' +
    str(averageDifference))

if __name__ == '__main__':
  run_average_heuristic()
