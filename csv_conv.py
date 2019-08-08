#!/usr/bin/env python
import sys
import io
import codecs
from pytz import timezone

def print_help():
    # print help message
    print >> sys.stderr, "Usage: csv_conv.py [Options] <filename>"
    print >> sys.stderr, "Options and arguments:"
    print >> sys.stderr, "  [-h/--help]: Show this message."
    print >> sys.stderr, "  [-s]: Define sperator. Defaults to comma."
    print >> sys.stderr, "  [-q]: Define text qualifier. Defaults to auto detect."
    print >> sys.stderr, "  [-t]: Trim white space at the beginning and end of each field. Defaults to double quote."
    print >> sys.stderr, "  [-z]: Specify timezone for time fields. Defaults to server timezone. Can also be Asia/Chongqing etc."
    print >> sys.stderr, "        For standard timezone names, refer to: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"
    print >> sys.stderr, "  [-k]: Skip errors and continue parsing following lines."
    print >> sys.stderr, "  <filename>: csv file name."

def get_parameters():
    # get parameter from command line
    args = {
        "-s": ",",
        "-q": '"',
        "-t": True,
        "-k": True
    }
    if len(sys.argv) > 1:
        for i in range(0, len(sys.argv)):
            p = sys.argv[i]
            if len(sys.argv) > i + 1:
                if p == '-s':
                    args['-s'] = sys.argv[i + 1]
                elif p == '-q':
                    val = sys.argv[i + 1]
                    # only ' or " can be used as qualifier
                    if val == "'":
                        args['-q'] = "'"
                    else:
                        args['-q'] = '"'
                elif p == '-t':
                    val = sys.argv[i + 1].lower()
                    if val == 'false':
                        args['-t'] = False
                elif p == '-z':
                    args['-z'] = sys.argv[i + 1]
                elif p == '-k':
                    val = sys.argv[i + 1].lower()
                    if val == 'false':
                        args['-k'] = False
                    
    return args

# Define a state machine to identify csv fields
STATES = {
    "qualifier": "qualifier",
    "qualifier_close": "qualifier_close",
    "seperator": "seperator",
    "field": "field",
    "field_in_qualifier": "field_in_qualifier",
    "end": "end"
}

class CSVStateMachine:
    def __init__(self, args, output):
        self.seperator = args['-s']
        self.qualifier = args['-q']
        self.trim = args['-t']
        # self.timezone = args['-z']
        self.skip_error = args['-k']
        self.output = output
        self.state = STATES["qualifier"]
        # input buffer for whole input line.
        self.buff = ""
        # position of character done recognizing
        self.base_pos = 0
        self.fields = []
        self.encoding = 'utf8'
    def feed(self, buff):
        self.state = STATES["qualifier"]
        self.fields = []
        self.base_pos = 0
        self.buff = buff
        length = len(buff)
        while self.base_pos < length:
            self.state_qualifier()
            self.state_qualifier_close()
            self.state_seperator()
            self.state_field()
            self.state_field_in_qualifier()
            self.state_end()
        if self.state != STATES["end"]:
            print >> sys.stderr, "Couldn't parse this line: {0}".format(line)
            if not self.skip_error:
                print >> sys.stderr, "-k set to stop on error. exiting..."
                exit()

    def state_qualifier(self):
        if self.state == STATES["qualifier"]:
            # TODO: BOM is not properly handled here. Fix it!
            string = self.buff[self.base_pos:self.base_pos + len(self.qualifier)]
            if string == self.qualifier and self.qualifier != "":
                # recognized qualifier
                self.base_pos = len(self.qualifier)
                self.state = STATES["field_in_qualifier"]
            else:
                self.state = STATES["field"]
    def state_qualifier_close(self):
        if self.state == STATES["qualifier_close"]:
            self.base_pos += len(self.qualifier)
            i = self.base_pos + 1
            string = self.buff[self.base_pos:i]
            if string in ['\r', '\n', '']:
                self.state = STATES["end"]
            else:
                self.state = STATES["seperator"]
    def state_seperator(self):
        if self.state == STATES["seperator"]:
            i = self.base_pos + len(self.seperator)
            string = self.buff[self.base_pos:i]
            if string == self.seperator:
                self.base_pos = i
                self.state = STATES["qualifier"]
            # else:
                # Shouldn't happen since this is handled in "qualifier" state
    def state_field(self):
        if self.state == STATES["field"]:
            i = self.base_pos + 1
            string = self.buff[self.base_pos:i]
            if string in ['\r', '\n', '']:
                # last field is empty
                self.push_field("")
                self.state = STATES["end"]
            else:
                for i in range(self.base_pos, len(self.buff) - len(self.qualifier)):
                    j = i + len(self.seperator)
                    string = self.buff[i:j]
                    if string == self.seperator:
                        field = self.buff[self.base_pos:i]
                        self.push_field(field)
                        self.state = STATES["seperator"]
                        self.base_pos = i
                        break
                    else:
                        j = i + 1
                        string = self.buff[i:j]
                        if string in ['\r', '\n']:
                            # end of line
                            field = self.buff[self.base_pos:i]
                            self.push_field(field)
                            self.state = STATES["end"]
                            break

    def state_field_in_qualifier(self):
        if self.state == STATES["field_in_qualifier"]:
            for i in range(self.base_pos, len(self.buff) - len(self.qualifier)):
                j = i + len(self.qualifier)
                if self.buff[i:j] == self.qualifier:
                    # closing qualifier detected
                    # if it's followed by a seperator or line end then it's qualified
                    # otherwise it should be a normal field charactor
                    k = j + len(self.seperator)
                    afterStr = self.buff[j:j+1]
                    if self.buff[j:k] == self.seperator or afterStr in ['\r', '\n', '']:
                        field = self.buff[self.base_pos:i]
                        self.push_field(field)
                        self.state = STATES["qualifier_close"]
                        self.base_pos = i
                        break
                    else:
                        k = j + len(self.qualifier)
                        afterStr = self.buff[j:k]
                        k = j - len(self.qualifier)
                        beforeStr = self.buff[k:j]
                        if (afterStr == self.qualifier or beforeStr == self.qualifier) and self.qualifier != "":
                            continue
                        else:
                            # escape qualifier by repeat it once
                            self.buff = self.buff[:j] + self.qualifier + self.buff[j:]
                            self.base_pos += len(self.qualifier)
                            i += len(self.qualifier)
            if self.state == STATES["field_in_qualifier"]:
                # searched to the end still can't find closing qualifier. something is wrong.
                self.base_pos = len(self.buff)
    def state_end(self):
        if self.state == STATES["end"]:
            self.base_pos = len(self.buff)
            line = ",".join(map(lambda f: '"{0}"'.format(f) if f != "" else "", self.fields))
            try:
                line = line.decode(self.encoding)
            except UnicodeDecodeError:
                self.encoding = 'gbk'
                # print >> sys.stderr, line
                line = line.decode(self.encoding)
            line = line.encode(encoding='utf8',errors='strict')
            self.output .write(line)
            self.output.write("\n")
            self.output.flush()

    def push_field(self, field):
        # TODO: handle time convertion
        if self.trim:
            field = field.strip()
        self.fields.append(field)
    def detect_time(self):
        return

if __name__ == "__main__":
    if len(sys.argv) == 2 and (sys.argv[1] == "--help" or sys.argv[1] == '-h'):
        print_help()
        exit()

    fs = None
    if not sys.stdin.isatty():
        # stdin preferred
        fs = sys.stdin
    elif len(sys.argv) >= 2:
        # if stdin is not available, try last parameter as file name
        filename = sys.argv[len(sys.argv) - 1]
        try:
            fs = open(filename, 'r')
        except IOError:
            print >> sys.stderr, "File not found or occupied by other process: " + filename
            print_help()
            exit()
    else:
        print >> sys.stderr, "Can't find file to read from."
        print_help()
        exit()

    args = get_parameters()
    line = fs.readline()
    if not args.has_key('-q'):
        if line.startswith("'"):
            args['-q'] = "'"
        elif line.startswith('"'):
            args['-q'] = '"'
        else:
            args['-q'] = ""

    stateMachine = CSVStateMachine(args, sys.stdout)
    while(line != ""):
        stateMachine.feed(line)
        line = fs.readline()
