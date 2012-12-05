import json
from article import *
from parser import DELIMITER
from regression import read_articles,rank,get_pairs

def get_num_edits(filename):
  """ Returns a list whose elements are the number of edits for each article in
  the training set. """
  articles = read_articles(filename)
  numEdits = [article.num_edits() for article in articles]
  return numEdits

def run_average_heuristic():
  numEditsTrain = get_num_edits('train.json') 
  averageNumEdits = sum(numEditsTrain) / float(len(numEditsTrain))
  numEditsTest = get_num_edits('test.json')

  differences = []
  percentErrors = []
  rankTuples = []
  rankLabel = 0
  for editCount in numEditsTest:
    difference = abs(editCount - averageNumEdits)
    differences.append(difference)

    percentError = round(100 * float(abs(editCount - averageNumEdits)) / editCount, 
      2)
    percentErrors.append(percentError)

    rankTuples.append((rankLabel, editCount, averageNumEdits))
    rankLabel += 1

  totalDifference = sum(differences)
  averageDifference = sum(differences) / float(len(differences))
  averageError = sum(percentErrors) / len(percentErrors)

  rankedByActualEdits = rank(rankTuples, 1)
  rankedByPredictedEdits = rank(rankTuples, 2)
  
  rankedByActualEditPairs = get_pairs(rankedByActualEdits)
  rankedByPredictedEditPairs = get_pairs(rankedByPredictedEdits)

  intersectionOfRankPairs = rankedByActualEditPairs.intersection(rankedByPredictedEditPairs)
  print(len(intersectionOfRankPairs))
  print(len(rankedByActualEditPairs))
  rankScore = (float(len(intersectionOfRankPairs)) / len(rankedByActualEditPairs))

  print('Average difference between actual and predicted values: ' +
    str(averageDifference))
  print('Average error: ' + str(averageError) + '%')
  print('Ranking score: ' + str(rankScore) + '%')

if __name__ == '__main__':
  run_average_heuristic()
