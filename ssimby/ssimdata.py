''' Data classes for use with SSIMby. '''

import datetime

# function to map slice parameters to spec parameters


def slicer(first, last):
  return slice(first - 1, last)

# FLIGHT LEG RECORD (200 bytes)


class FlightLegRecord:
  def __init__(self, line):
    self.record_type = line[slicer(1, 1)]
    self.op_suffix = line[slicer(2, 2)]
    self.flight_des = line[slicer(3, 9)]
    self.airline_des = line[slicer(3, 5)]
    self.flight_num = line[slicer(6, 9)]
    self.itinerary_var_id = line[slicer(10, 11)]
    self.leg_seq_num = line[slicer(12, 13)]
    self.service_type = line[slicer(14, 14)]
    self.op_period = line[slicer(15, 28)]
    self.op_days = line[slicer(29, 35)]
    self.freq_rate = line[slicer(36, 36)]
    self.dep_station = line[slicer(37, 39)]
    self.dep_pax_std = line[slicer(40, 43)]
    self.dep_sched_time = insert(line[slicer(44, 47)], ':', 2)
    self.dep_utc_variation=line[slicer(48, 52)].strip()
    self.dep_pax_terminal=line[slicer(53, 54)]
    self.arr_station=line[slicer(55, 57)]
    self.arr_sched_time = insert(line[slicer(58, 61)], ':', 2)
    self.arr_pax_sta=line[slicer(62, 65)]
    self.arr_utc_variation=line[slicer(66, 70)].strip()
    self.arr_pax_terminal=line[slicer(71, 72)]
    self.ac_type_iata=line[slicer(73, 75)]
    self.pax_rsvp_book_des=line[slicer(76, 95)]
    self.pax_rsvp_book_mod=line[slicer(96, 100)]
    self.meal_note=line[slicer(101, 110)]
    self.joint_op_airline_des=line[slicer(111, 119)]
    self.min_connect_time_intdom_status=line[slicer(120, 121)]
    # spare
    self.itinerary_var_id_overflow=line[slicer(128, 128)]
    self.ac_owner=line[slicer(129, 131)]
    self.cockpit_crew_employer=line[slicer(132, 134)]
    self.cabin_crew_employer=line[slicer(135, 137)]
    self.onward_flight=line[slicer(138, 146)]
    self.airline_des=line[slicer(138, 140)]
    self.flight_num=line[slicer(141, 144)]
    self.aircraft_rotation_layover=line[slicer(145, 145)]
    self.op_suffix=line[slicer(146, 146)]
    # spare
    self.flight_transit_layover=line[slicer(148, 148)]
    self.code_sharing=line[slicer(149, 149)]
    self.traffic_restrict_code=line[slicer(150, 160)]
    self.traffic_restrict_code_leg_oflow=line[slicer(161, 161)]
    # spare
    self.aircraft_config=line[slicer(173, 192)]
    self.date_var=line[slicer(193, 194)]
    self.record_serial_num=line[slicer(195, 200)].strip()

    self.arr_local_date=None
    self.dep_local_date=None
    self.utc_dep_date=None
    self.utc_arr_date=None

    self.dep_airport = None
    self.arr_airport = None

  def export(self, eol='\n'):
    content = [
      self.flight_des,
      self.leg_seq_num,
      self.op_period,
      self.op_days,
      self.dep_station,
      self.dep_sched_time,
      self.dep_utc_variation,
      self.arr_station,
      self.arr_sched_time,
      self.arr_utc_variation,
      self.ac_type_iata,

      self.dep_local_date.strftime('%Y-%m-%d %H:%M'),
      self.arr_local_date.strftime('%Y-%m-%d %H:%M'),
      self.utc_dep_date.strftime('%Y-%m-%d %H:%M'),
      self.utc_arr_date.strftime('%Y-%m-%d %H:%M'),
      self.aircraft_config.strip()]

    if self.dep_airport != None and self.arr_airport != None:
      content += [self.dep_airport.export(), self.arr_airport.export()]

    return '\t'.join(content) + eol

  @staticmethod
  def header(eol, has_airports=False):
    content = [
      'flight_des',
      'leg_seq_num',
      'op_period',
      'op_days',
      'dep_station',
      'dep_sched_time',
      'dep_utc_variation',
      'arr_station',
      'arr_sched_time',
      'arr_utc_variation',
      'ac_type_iata',

      'dep_local_date',
      'arr_local_date',
      'utc_dep_date',
      'utc_arr_date',

      'aircraft_config'
    ]
    if has_airports:
      content.append(Airport.header('dep_'))
      content.append(Airport.header('arr_'))

    return '\t'.join(content)[0]



class Airport():
  def __init__(self, line, hidx):
    split_line = line.split('\t') if '\t' in line else line.split(',')

    self.latitude = split_line[hidx['latitude']]
    self.longitude = split_line[hidx['longitude']]
    self.name = split_line[hidx['airport']]
    self.country = split_line[hidx['country']]
    self.iata = split_line[hidx['iata']]
    self.icao = split_line[hidx['icao']]
  
  @staticmethod
  def get_header_indices(header):
    split_header = header.split('\t') if '\t' in header else header.split(',')
    header_indices = {
      'latitude': -1,
      'longitude': -1,
      'icao': -1,
      'iata': -1,
      'airport': -1,
      'country': -1,
    }
    # get the locations of all columns that match the keys
    for column in header_indices.keys():
      for i,hcolumn in enumerate(split_header):
        # match if the key is in the column header (case insensitive)
        if column.lower() in hcolumn.lower():
          header_indices[column] = i
          break
    return header_indices

  def export(self):
    return '\t'.join([
      self.latitude,
      self.longitude,
      self.icao,
      self.name,
      self.country
    ])

  @staticmethod
  def header(prefix=''):
    return '\t'.join([
      prefix + 'latitude',
      prefix + 'longitude',
      prefix + 'icao',
      prefix + 'airportname',
      prefix + 'country'])
        

months = {
  'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4,
  'MAY': 5, 'JUN': 6, 'JUL': 7, 'AUG': 8,
  'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
}

def datestring_to_date(datestr):
  if (datestr == '00XXX00'):
    return datetime.date(2100, 1, 1)
  day=int(datestr[0:2])
  month=months[datestr[2:5]]
  year=2000 + int(datestr[5:7])
  return datetime.date(day=day, month=month, year=year)

def hour24_to_time(hour24):
  hours=int(hour24[:2])
  minutes=int(hour24[3:])
  return datetime.time(hours, minutes)

def offset_utc(dt, offset):
  if offset == 0:
    return dt
  return datetime.timedelta(hours=-1*offset/100) + dt


def insert(source_str, insert_str, pos):
  return source_str[:pos] + insert_str + source_str[pos:]
