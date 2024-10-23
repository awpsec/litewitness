# litewitness
lightweight web screenshot tool

installation:

download zip, or git clone

```chmod +x setup.sh```

```./setup.sh```

```source lite-witness-env/bin/activate```

```./setup.sh```

ready to go!

```
 ,--.  _   _   __  _ .--.   .--.  .---.  .---.
`'_\ :[ \ [ \ [  ][ '/'`\ \( (`\]/ /__\/ /'`\]
// | |,\ \/\ \/ /  | \__/ | `'.'.| \__.,| \__.
'-;__/ \__/\__/   | ;.__/ [\__) )'.__.''.___.'
                  [__|
                       ) o _)_ _        o _)_ _   _   _  _
                      (  ( (_ )_) )_)_) ( (_ ) ) )_) (  (
                             (_                 (_   _) _)

usage: litewitness.py [-h] -x INPUT -o OUTPUT [-timeout TIMEOUT] [-v]

litewitness: a lightweight web screenshot tool

options:
  -h, --help            show this help message and exit
  -x INPUT, --input INPUT
                        path to the input file with URLs/IPs
  -o OUTPUT, --output OUTPUT
                        output folder for screenshots and logs
  -timeout TIMEOUT      page load timeout in seconds (default: 3)
  -v, --verbose         enable verbose output
```
