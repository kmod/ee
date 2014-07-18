# import gdata.spreadsheet.service
# s = gdata.spreadsheet.service.SpreadsheetsService()

import collections
from cStringIO import StringIO
import csv
import os
import urllib

BOARD_VGA_V0_3 = "VGA v0.3"
BOARD_TEST_SOCKET = "Test Socket"
BOARD_A13_V0_1 = "A13 v0.1"

GIDS = {
    BOARD_VGA_V0_3 : 1541628867,
    BOARD_TEST_SOCKET : 1284680577,
    BOARD_A13_V0_1 : 117879415,
}

def get_bom_csv(name):
    cache_fn = "%s.bom" % name
    if os.path.exists(cache_fn):
        with open(cache_fn) as f:
            return f.read()

    print "Fetching %s from google docs..." % name
    csv_str = urllib.urlopen("https://docs.google.com/feeds/download/spreadsheets/Export?key=11qjRIftDNWsL_nn-W00stsIar9J9Ye0ja20ET1VebuY&exportFormat=csv&gid=%d" % GIDS[name]).read()

    with open(cache_fn, 'w') as f:
        f.write(csv_str)
    return csv_str

BomLine = collections.namedtuple("BomLine", ["qty", "value", "device", "package", "parts", "description", "attributes"])

def parse_csv(csv_str):
    csv_reader = csv.reader(StringIO(csv_str), delimiter=',', quotechar='"')

    parsed = list(csv_reader)
    attribute_names = parsed[6:]
    rtn = []
    for row in parsed[1:]:
        row[0] = int(row[0])
        bl = BomLine(*row[:6] + [row[6:]])

        rtn.append(bl)
        print bl
    return rtn

parse_csv(get_bom_csv(BOARD_A13_V0_1))

