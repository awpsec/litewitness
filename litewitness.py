from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import argparse
import time
import os
import pyfiglet
from colorama import Fore, Style

banner = r"""
 ,--.  _   _   __  _ .--.   .--.  .---.  .---.
`'_\ :[ \ [ \ [  ][ '/'`\ \( (`\]/ /__\/ /'`\]
// | |,\ \/\ \/ /  | \__/ | `'.'.| \__.,| \__.
'-;__/ \__/\__/   | ;.__/ [\__) )'.__.''.___.'
                  [__|
                       ) o _)_ _        o _)_ _   _   _  _
                      (  ( (_ )_) )_)_) ( (_ ) ) )_) (  (
                             (_                 (_   _) _)
"""
print(Fore.GREEN + banner + Style.RESET_ALL)

def capture_screenshot(url, driver, output_folder, verbose):
    try:
        driver.get(url)
        time.sleep(3)  # Give the page some time to load
        filename = url.replace("http://", "").replace("https://", "").replace("/", "_") + ".png"
        screenshot_path = os.path.join(output_folder, filename)
        driver.save_screenshot(screenshot_path)

        if verbose:
            print(f"{url} = captured screenshot")

        return True, url
    except TimeoutException:
        if verbose:
            print(f"{url} = failed")

        return False, url

def main(input_file, output_folder, timeout, verbose):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set the path to Chromium binary
    chrome_options.binary_location = "/usr/bin/chromium"

    # Manually specify the ChromeDriver path
    driver = webdriver.Chrome(
        service=Service("/usr/bin/chromedriver"),  # Manually set the path to the installed ChromeDriver
        options=chrome_options
    )
    driver.set_page_load_timeout(timeout)

    # Prepare output folder with error handling
    try:
        if not os.path.exists(output_folder):
            print(f"Creating output folder: {output_folder}")
            os.makedirs(output_folder, exist_ok=True)
        else:
            print(f"Using existing output folder: {output_folder}")
    except Exception as e:
        print(f"Error creating output folder: {e}")

    # Prepare log files
    success_log = os.path.join(output_folder, "success.txt")
    fail_log = os.path.join(output_folder, "fail.txt")

    # Clear previous log contents (if any)
    try:
        open(success_log, 'w').close()
        print(f"Created success log at: {success_log}")
        open(fail_log, 'w').close()
        print(f"Created fail log at: {fail_log}")
    except Exception as e:
        print(f"Error creating log files: {e}")

    # Read the IPs/URLs from the input file
    with open(input_file, 'r') as file:
        urls = file.read().splitlines()

    for url in urls:
        print(f"Processing {url}...")  # Add this to check each URL/IP being processed
        success, logged_url = capture_screenshot(url, driver, output_folder, verbose)

        if success:
            with open(success_log, 'a') as success_file:
                success_file.write(f"{logged_url} = captured screenshot\n")
        else:
            with open(fail_log, 'a') as fail_file:
                fail_file.write(f"{logged_url} = failed\n")

    driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ZeddWitness: A lightweight web screenshot tool")
    parser.add_argument("-x", "--input", required=True, help="Path to the input file with URLs/IPs")
    parser.add_argument("-o", "--output", required=True, help="Output folder for screenshots and logs")
    parser.add_argument("-timeout", type=int, default=3, help="Page load timeout in seconds (default: 3)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    args = parser.parse_args()

    # Call the main function
    main(args.input, args.output, args.timeout, args.verbose) 
