# litewitness
lightweight web screenshot tool

#installation

download zip, or git clone

```chmod +x setup.sh```

```./setup.sh```

```source lite-witness-env/bin/activate```

```./setup.sh```

ready to go!

make sure you're creating a new folder to store the outfiles in (screenshots, success.txt and fail.txt)

```

 ,--.  _   _   __  _ .--.   .--.  .---.  .---.
`'_\ :[ \ [ \ [  ][ '/'`\ \( (`\]/ /__\/ /'`\)
// | |,\ \/\ \/ /  | \__/ | `'.'.| \__.,| \__.
'-;__/ \__/\__/   | ;.__/ [\__) )'.__.''.___.'
                  [__|
                       ) o _)_ _        o _)_ _   _   _  _
                      (  ( (_ )_) )_)_) ( (_ ) ) )_) (  (
                             (_                 (_   _) _)

usage: litewitness.py [-h] [-x INPUT] [-xml XMLFILE] -o OUTPUT [-timeout TIMEOUT] [-ss SCREENSHOTCOUNT]
                      [-j JITTER] [-v] [-sf SUCCESSFILE] [-ff FAILFILE]

litewitness: a lightweight web screenshot tool

options:
  -h, --help            show this help message and exit
  -x INPUT, --input INPUT
                        path to the input file with URLs/IPs
  -xml XMLFILE, --xmlfile XMLFILE
                        path to the Nmap XML file
  -o OUTPUT, --output OUTPUT
                        output folder for screenshots and logs
  -timeout TIMEOUT      page load timeout in seconds (default: 3)
  -ss SCREENSHOTCOUNT, --screenshotcount SCREENSHOTCOUNT
                        number of screenshots per webpage (default: 1)
  -j JITTER, --jitter JITTER
                        jitter value to randomize delay between scans (default: 0)
  -v, --verbose         enable verbose output
  -sf SUCCESSFILE, --successfile SUCCESSFILE
                        path to success log file (default: success.txt in output folder)
  -ff FAILFILE, --failfile FAILFILE
                        path to failure log file (default: fail.txt in output folder)
```

# usage

have to specify flags: -x or -xml & -o

all other flags are optional, include ports inside of the input file otherwise it will test 80/443. 
all ports besides 443 will be reached using http.

