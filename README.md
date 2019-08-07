# csv_conv

This script uses state machine to normalize csv file for mongoimport to work properly.

```bash
Usage: csv_conv.py [Options] <filename>
Options and arguments:
  [-h/--help]: Show this message.
  [-s]: Define sperator. Defaults to comma.
  [-q]: Define text qualifier. Defaults to auto detect.
  [-t]: Trim white space at the beginning and end of each field. Defaults to true.
  <filename>: csv file name.
```
