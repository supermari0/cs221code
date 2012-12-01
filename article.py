import json

class Article:
  def __init__(self, filepath):
    file = open(filepath, 'r')
    self.data = json.loads(file.read())
    file.close()

  def basic_feature_vector(self):
    # Returns an array of features for the article
    return [self.title(), self.headings(), self.body_text(), self.body_length()] + \
           [self.links(), self.is_current_event(), self.percent_anonymous_edits()] + \
           [self.percent_top_edits(), self.top_editors(), self.age()]

  def title(self):
    return self.data['title']

  def headings(self):
    return self.data['body']['headings']

  def body_text(self):
    return self.data['body']['text']

  def body_length(self):
    return self.data['body']['length']

  def links(self):
    return self.data['links']

  def is_current_event(self):
    return self.data.has_key('is_current_event') and self.data['is_current_event']

  def num_edits(self):
    return self.data['edits']['total']

  def num_anonymous_edits(self):
    return self.data['edits']['anonymous']

  def percent_anonymous_edits(self):
    # Returns a number between 0% and 100%
    return float(self.num_anonymous_edits()) / float(self.num_edits()) * 100.0

  def num_edits_by_top(self):
    # Returns the number of edits by the top 10 percent
    return self.data['edits']['top_10_percent']

  def percent_top_edits(self):
    # Returns a number between 0% and 100%
    return float(self.num_edits_by_top()) / float(self.num_edits()) * 100.0

  def edit_frequency(self):
    return self.data['edits']['frequency']

  def top_editors(self):
    return [editor['username'] for editor in self.data['top_editors']]

  def age(self):
    return self.data['age']
