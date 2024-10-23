import os
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import time
import pyfiglet
from colorama import Fore, Style

banner = r"""
 ,--.  _   _   __  _ .--.   .--.  .---.  .---.
`'_\ :[ \ [ \ [  ][ '/'`\ \( (`\]/ /__\/ /'`\)
// | |,\ \/\ \/ /  | \__/ | `'.'.| \__.,| \__.
'-;__/ \__/\__/   | ;.__/ [\__) )'.__.''.___.'
                  [__|
                       ) o _)_ _        o _)_ _   _   _  _
                      (  ( (_ )_) )_)_) ( (_ ) ) )_) (  (
                             (_                 (_   _) _)
"""
print(Fore.LIGHTBLACK_EX + banner + Style.RESET_ALL)

def capture_screenshot(url, driver, output_folder, verbose):
    try:
        driver.get(url)
        time.sleep(3)  # give the page some time to load

        # sanitize URL or IP for file naming
        filename = url.replace("http://", "").replace("https://", "").replace("/", "_").replace(":", "_") + ".png"
        screenshot_path = os.path.join(output_folder, filename)

        driver.save_screenshot(screenshot_path)
        
        if verbose:
            print(f"{url} = captured screenshot")

        return True, url
    except TimeoutException:
        if verbose:
            print(f"{url} = failed")

        return False, url

# main function
def main(input_file, output_folder, timeout, verbose, success_log, fail_log):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # set the path to Chromium binary
    chrome_options.binary_location = "/usr/bin/chromium"

    # manually specify the ChromeDriver path
    driver = webdriver.Chrome(
        service=Service("/usr/bin/chromedriver"),
        options=chrome_options
    )
    driver.set_page_load_timeout(timeout)

    # prepare output folder with error handling
    try:
        if not os.path.exists(output_folder):
            print(f"creating output folder: {output_folder}")
            os.makedirs(output_folder, exist_ok=True)
        else:
            print(f"using existing output folder: {output_folder}")
    except Exception as e:
        print(f"error creating output folder: {e}")

    # clear previous log contents (if any)
    try:
        open(success_log, 'w').close()
        print(f"created success log at: {success_log}")
        open(fail_log, 'w').close()
        print(f"created fail log at: {fail_log}")
    except Exception as e:
        print(f"error creating log files: {e}")

    # read the IPs/URLs from the input file
    with open(input_file, 'r') as file:
        urls = file.read().splitlines()

    for url in urls:
        print(f"Processing {url}...")  # add this to check each URL/IP being processed
        success, logged_url = capture_screenshot(url, driver, output_folder, verbose)
        
        # log success or failure
        if success:
            with open(success_log, 'a') as success_file:
                success_file.write(f"{logged_url} = captured screenshot\n")
        else:
            with open(fail_log, 'a') as fail_file:
                fail_file.write(f"{logged_url} = failed\n")

    driver.quit()

# argument parser
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="litewitness: a lightweight web screenshot tool")
    parser.add_argument("-x", "--input", required=True, help="path to the input file with URLs/IPs")
    parser.add_argument("-o", "--output", required=True, help="output folder for screenshots and logs")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable verbose output")
    parser.add_argument("-sf", "--successfile", default="success.txt", help="path to success log file (default: success.txt in output folder)")
    parser.add_argument("-ff", "--failfile", default="fail.txt", help="path to failure log file (default: fail.txt in output folder)")
    parser.add_argument("-timeout", type=int, default=3, help="page load timeout in seconds (default: 3)")
    
    args = parser.parse_args()

    # if the success/fail file is not an absolute path, put it in the output folder
    success_log = args.successfile if os.path.isabs(args.successfile) else os.path.join(args.output, args.successfile)
    fail_log = args.failfile if os.path.isabs(args.failfile) else os.path.join(args.output, args.failfile)

    # call the main function
    main(args.input, args.output, args.timeout, args.verbose, success_log, fail_log)
