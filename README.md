# CmdTools
I seem to be writing the same tools from scratch over and over again, so it would be a good idea to just make one good version.

This program filters lines in a file based on the values in one of the columns. These values can be provided in a file or as a comma-separated string.

There are a range of matching functions like contains, greater and less, exact match, and starts/ends with. Columns can be specified using their 0-based index or by specifying the name in the header to determine the index at runtime.

Supports some other nice features like ignoring letter case, excluding headers from output, specifying custom delimiters (including multi-character delimiters), verbose mode logging, and a useful help screen.

## Installation
Download the files and install locally with pip. Requires Python 3 (may work with Python 2, but haven't checked) and the `click` package (this should be installed automatically because it's a required package).

`pip install .`

You can also just copy and paste the files around, but that's not a very good approach.
Once installed, run `filefilter -h` or `filefilter --help` in the terminal for usage instructions.

## Usage
This is what the help screen shows.
```
Usage: filefilter [OPTIONS] IN_FILE VALUES OUT_FILE

  Filter lines in a file based on the values of a single column.

  Supports a variety of string matching functions.

  VALUES must be a file path (each value on a new line) or as a comma-
  separated sequence of words.

Options:
  -d, --delimiter TEXT            Delimiter to use in the files. Default is
                                  TAB.
  -x, --column-index INTEGER      Column index to use. Default is 0.
  -n, --column-name TEXT          Find column by name. Takes precedence over
                                  --column-index.
  -m, --match [exact|starts|ends|contains|greater|less]
                                  The method used to match values. Default is
                                  "exact".
  -f, --file-values               Read values as a file path.
  -i, --ignore-case               Ignores letter case when searching and
                                  matching.
  -e, --no-header                 Excludes the header from the output.
  --verbose                       Enables information-dense terminal output.
  --version                       Show the version and exit.
  -h, --help                      Show this message and exit.
```

## Examples
Using the sample files, an example filter is:

`filefilter --column-name STATUS --ignore-case --file-values test-files/sample-input.txt test-files/sample-values.txt test-files/sample-output.txt`

The same, but using short commands:

` filefilter -n STATUS -if test-files/sample-input.txt test-files/sample-values.txt test-files/sample-output.txt `

This uses exact matching by default, ignoring case and using a file as the input for values. It will save all lines that have either _STORED_, _SCRAPPED_, or _RETIRED_ in the _STATUS_ column (keeping the header).

## Notes
- Reads and keeps line ending style of the original file.
- Default delimiter is TAB, but if no tabs found it will default to COMMAS.
- If using a custom delimiter with letters, --ignore-case also applies to this, e.g. `... -i -d BBB ...` will effectively be `... -i -d bbb ...` as lowercase is used for case-insensitive comparisons.

## To-do (maybe)
- Add in stdin and stdout options rather than just requiring files. However, because this program can be replaced with a well-made awk script, the focus was on files because Windows ain't got no awk.