import json

class Article:
  def __init__(self, json_string):
    self.data = json.loads(json_string)

  def title(self):
    return self.data['title']

  def headings(self):
    return self.data['body']['headings']

  # def body_text(self):
  #   return self.data['body']['text']

  def body_length(self):
    return self.data['body']['length']

  def links(self):
    # Returns a list of dictionaries with keys 'name' and 'number_of_mentions'
    return self.data['links']

  def link_names(self):
    return [link['name'] for link in self.links()]

  def link_number_of_mentions(self):
    return [link['number_of_mentions'] for link in self.links()]

  # def is_current_event(self):
  #   return self.data.has_key('is_current_event') and self.data['is_current_event']

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

  # def age(self):
  #   return self.data['age']

  # def body_text_tokens(self):
  #   return self.body_text().lower().split()

  def heading_tokens(self):
    return ' '.join(self.headings()).lower().split()
