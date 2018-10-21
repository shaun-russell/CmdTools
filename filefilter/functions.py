''' File for storing classes related to reusable functions '''

class MatchTypes:
  @staticmethod
  def match_exact(data, segment):
    ''' data is equal to segment '''
    return data == segment

  @staticmethod
  def match_starts(data, segment):
    ''' data starts with segment '''
    return data.startswith(segment)

  @staticmethod
  def match_ends(data, segment):
    ''' data ends with segment '''
    return data.endswith(segment)

  @staticmethod
  def match_contains(data, segment):
    ''' data contains segment '''
    return segment in data

  @staticmethod
  def match_greater(data, segment):
    ''' data is greater than the segment (value) '''
    if data.isnumeric() and segment.isnumeric():
      return float(data) > float(segment)
    else:
      return data > segment

  @staticmethod
  def match_less(data, segment):
    ''' data is less than the segment (value) '''
    if data.isnumeric() and segment.isnumeric():
      return float(data) < float(segment)
    else:
      return data > segment


def remove_newline(text):
  return text.replace('\r', '').replace('\n', '')