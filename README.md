# csv_conv

## Instruction

This script uses state machine to fix csv file for `mongoimport` to work properly.

```txt
Usage: csv_conv.py [Options] <filename>
Options and arguments:
  [-h/--help]: Show this message.
  [-s]: Define sperator. Defaults to comma.
  [-q]: Define text qualifier. Defaults to auto detect.
  [-t]: Trim white space at the beginning and end of each field. Defaults to double quote.
  [-z]: Specify timezone for time fields. Defaults to server timezone. Can also be Asia/Chongqing etc.
        For standard timezone names, refer to: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
  [-k]: Skip errors and continue parsing following lines.
  <filename>: csv file name.
```

## Scenarios

### Quote within quote

Quotes should be immediated followed by seperator or line end or EOF, otherwise it's not a valid qualifier, and should be escaped. The following format should be fixed (_See `../testcase/test_case_1.csv`_):

```csv
"What""s up!","I"m good",I"m also good,"I'm still good"","two quotes" shouldn't make any difference""
```

```bash
./csv_conv.py ../testcase/test_case_1.csv
"What""s up!","I""m good","I""m also good","""I'm still good""","two quotes"" shouldn't make any difference"""
```

### Begin/End with white space

For fields that begin/end with white space are stript by default. Otherwise `mongoimport` type conversion wouldn't work properly (_See `../testcase/test_case_2.csv`_):

```csv
 red,	yellow,green ,"red	"
 ```

```bash
./csv_conv.py ../testcase/test_case_2.csv
"red","yellow","green","red"
```

If it's not expected behavior, use `-t false` to cancel it.

### Customize seperator

Seperator can be customized, not necessarily to be ",". Specify seperator by `-s`. Note that seperators like `|` needs to be escaped in bash. E.g. (_See `../testcase/test_case_3.csv`_):

```csv
"hello"||"This is a test"||"This should be good.||"||""
```

```bash
./csv_conv.py -s '||' ../testcase/test_case_3.csv
"hello","This is a test","This should be good.||""",
```

### Encoding detect

For now `GBK` can be detected and converted to `UTF-8`. Will add other encoding detected later.
