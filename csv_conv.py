#!/usr/bin/env python
import sys
import io

def print_help():
    # print help message
    print >> sys.stderr, "Usage: csv_conv.py [Options] <filename>"
    print >> sys.stderr, "Options and arguments:"
    print >> sys.stderr, "  [-h/--help]: Show this message."
    print >> sys.stderr, "  [-s]: Define sperator. Defaults to comma."
    print >> sys.stderr, "  [-q]: Define text qualifier. Defaults to auto detect."
    print >> sys.stderr, "  [-t]: Trim white space at the beginning and end. Defaults to true."
    print >> sys.stderr, "  <filename>: csv file name."

def get_parameters():
    # get parameter from command line
    args = {
        "-s": ",",
        "-t": True
    }
    if len(sys.argv) > 1:
        for i in range(0, len(sys.argv)):
            p = sys.argv[i]
            if len(sys.argv) > i + 1:
                if p == '-s':
                    args['-s'] = sys.argv[i + 1]
                elif p == '-q':
                    args['-q'] = sys.argv[i + 1]
                elif p == '-t':
                    val = sys.argv[i + 1].lower()
                    if val == 'false': args['-t'] = False
                    else: args['-t'] = True
                    
    return args

if len(sys.argv) == 2 and (sys.argv[1] == "--help" or sys.argv[1] == '-h'):
    print_help()
    exit()

fs = None
if not sys.stdin.isatty():
    # stdin preferred
    fs = sys.stdin
elif len(sys.argv) >= 2:
    # if stdin is not available, try last parameter as file name
    try:
        fs = open(sys.argv[len(sys.argv) - 1], 'r')
    except IOError:
        print >> sys.stderr, "File not found or occupied by other process."
        print_help()
        exit()
else:
    print >> sys.stderr, "Can't find file to read from."
    print_help()
    exit()

args = get_parameters()
line = fs.readline()
if not args.has_key['-q']:
    if line.startswith("'"):
        args['-q'] = "'"
    elif line.startswith('"'):
        args['-q'] = '"'


# Define a state machine to identify csv fields
STATES = {
    "start": 0,
    "qualifier": 1,
    "seperator": 2,
}
SUB_STATES = {
    "none": 0,
    "pre_seperator": 1,
    "seperator": 2,
    "end_seperator": 3,
    "qualifier": 4
}

class CSVStateMachine:
    def __init__(self, s, q, output):
        self.seperator = s
        self.qualifier = q
        self.output = output
        self.stat = STATES["start"]
        self.sub_stat = SUB_STATES["none"]
        self.queue_buff = []
        self.in_buff = ""
    def feed(self, byte):
        self.temp_buff += byte
        if self.in_buff == self.qualifier:
            self.stat = STATES["qualifier"]
            self.sub_stat = SUB_STATES["none"]
        # if self.state == STATS["start"]: