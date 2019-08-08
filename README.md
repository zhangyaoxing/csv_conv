# csv_conv

This script uses state machine to normalize csv file for mongoimport to work properly.

```txt
Usage: csv_conv.py [Options] <filename>
Options and arguments:
  [-h/--help]: Show this message.
  [-s]: Define sperator. Defaults to comma.
  [-q]: Define text qualifier. Defaults to auto detect.
  [-t]: Trim white space at the beginning and end of each field. Defaults to true.
  [-z]: Specify timezone for time fields. Defaults to server timezone. Can also be Asia/Chongqing etc.
        For standard timezone names, refer to: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
  <filename>: csv file name.
```
