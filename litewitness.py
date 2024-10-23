import os
import argparse
import random
import time
import xml.etree.ElementTree as ET
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from colorama import Fore, Style
import pyfiglet

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
print(Fore.LIGHTMAGENTA_EX + banner + Style.RESET_ALL)

def parse_nmap_xml(xml_file):
    hosts_with_ports = []
    tree = ET.parse(xml_file)
    root = tree.getroot()

    for host in root.findall('host'):
        ip = host.find('address').get('addr')
        for port in host.findall('.//port'):
            port_id = port.get('portid')
            protocol = 'https' if port_id == '443' else 'http'
            hosts_with_ports.append(f"{protocol}://{ip}:{port_id}")
    return hosts_with_ports

def capture_screenshot(url, driver, output_folder, verbose, screenshot_count):
    try:
        driver.get(url)
        time.sleep(3)

        for i in range(1, screenshot_count + 1):
            filename = url.replace("http://", "").replace("https://", "").replace("/", "_").replace(":", "_") + f"_{i}.png"
            screenshot_path = os.path.join(output_folder, filename)

            driver.save_screenshot(screenshot_path)

            if verbose:
                print(f"{url} = captured screenshot {i}/{screenshot_count}")

        return True, url
    except TimeoutException:
        if verbose:
            print(f"{url} = failed (timeout)")

        return False, url
    except WebDriverException as e:
        if verbose:
            print(f"{url} = failed (connection error: {str(e)})")

        return False, url

def main(input_file, xml_file, output_folder, timeout, jitter, verbose, success_log, fail_log, screenshot_count):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    chrome_options.binary_location = "/usr/bin/chromium"

    driver = webdriver.Chrome(
        service=Service("/usr/bin/chromedriver"),
        options=chrome_options
    )
    driver.set_page_load_timeout(timeout)

    try:
        if not os.path.exists(output_folder):
            print(f"creating output folder: {output_folder}")
            os.makedirs(output_folder, exist_ok=True)
        else:
            print(f"using existing output folder: {output_folder}")
    except Exception as e:
        print(f"error creating output folder: {e}")

    try:
        open(success_log, 'w').close()
        print(f"created success log at: {success_log}")
        open(fail_log, 'w').close()
        print(f"created fail log at: {fail_log}")
    except Exception as e:
        print(f"error creating log files: {e}")

    urls = []
    if xml_file:
        urls = parse_nmap_xml(xml_file)
    else:
        with open(input_file, 'r') as file:
            urls = file.read().splitlines()

    for url in urls:
        print(f"processing {url}...")

        if not url.startswith("http://") and not url.startswith("https://"):
            if ":443" in url:
                url = f"https://{url.split(':')[0]}:443"
            else:
                url = f"http://{url}"

        try:
            print(f"testing URL: {url}")
            
            success, logged_url = capture_screenshot(url, driver, output_folder, verbose, screenshot_count)

            if success:
                with open(success_log, 'a') as success_file:
                    success_file.write(f"{logged_url} = captured screenshot(s)\n")
            else:
                with open(fail_log, 'a') as fail_file:
                    fail_file.write(f"{logged_url} = failed\n")

            if jitter:
                time.sleep(random.uniform(0, jitter))

        except Exception as e:
            print(f"error while processing {url}: {e}")

    driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="litewitness: a lightweight web screenshot tool")
    parser.add_argument("-x", "--input", help="path to the input file with URLs/IPs")
    parser.add_argument("-xml", "--xmlfile", help="path to the Nmap XML file")
    parser.add_argument("-o", "--output", required=True, help="output folder for screenshots and logs")
    parser.add_argument("-timeout", type=int, default=3, help="page load timeout in seconds (default: 3)")
    parser.add_argument("-ss", "--screenshotcount", type=int, default=1, help="number of screenshots per webpage (default: 1)")
    parser.add_argument("-j", "--jitter", type=float, default=0, help="jitter value to randomize delay between scans (default: 0)")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable verbose output")
    parser.add_argument("-sf", "--successfile", default="success.txt", help="path to success log file (default: success.txt in output folder)")
    parser.add_argument("-ff", "--failfile", default="fail.txt", help="path to failure log file (default: fail.txt in output folder)")

    args = parser.parse_args()

    success_log = args.successfile if os.path.isabs(args.successfile) else os.path.join(args.output, args.successfile)
    fail_log = args.failfile if os.path.isabs(args.failfile) else os.path.join(args.output, args.failfile)

    main(args.input, args.xmlfile, args.output, args.timeout, args.jitter, args.verbose, success_log, fail_log, args.screenshotcount)

