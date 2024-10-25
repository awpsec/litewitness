#!/usr/bin/env python3

import os
import argparse
import random
import time
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from colorama import Fore, Style
import sys
import contextlib

banner = r"""
 ,--.  _   _   __  _ .--.   .--.  .---.  .---.
`'_\ :[ \ [ \ [  ][ '/'`\ \( (`\]/ /__\/ /'`\)
// | |,\ \/\ \/ /  | \__/ | `'.'.| \__.,| \__.
'-;__/ \__/\__/   | ;.__/ [\__) )'.__.''.___.'
                  [__|
                                litewitness ver. 2.2.9
"""

def print_banner():
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

@contextlib.contextmanager
def suppress_stdout_stderr():
    """A context manager that redirects stdout and stderr to devnull"""
    with open(os.devnull, 'w') as fnull:
        with contextlib.redirect_stdout(fnull), contextlib.redirect_stderr(fnull):
            yield

def setup_driver(timeout):
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--headless")
    
    firefox_options.set_preference("security.cert_pinning.enforcement_level", 0)
    firefox_options.set_preference("security.enterprise_roots.enabled", True)
    firefox_options.accept_insecure_certs = True

    with suppress_stdout_stderr():
        service = FirefoxService(GeckoDriverManager().install())

    driver = webdriver.Firefox(options=firefox_options, service=service)
    driver.set_page_load_timeout(timeout)
    return driver

def capture_screenshot(url, driver, output_folder, verbose, screenshot_count, full_page):
    try:
        driver.get(url)
        time.sleep(3)

        if full_page:
            driver.set_window_size(1920, 1080)
            width = driver.execute_script("return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);")
            height = driver.execute_script("return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);")
            driver.set_window_size(max(width, 1920), max(height, 1080))
        else:
            driver.set_window_size(1920, 1080)

        parsed_url = urlparse(url)
        port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)

        for i in range(1, screenshot_count + 1):
            filename = f"{parsed_url.hostname}_p{port}_{i}.png"
            screenshot_path = os.path.join(output_folder, filename)
            driver.save_screenshot(screenshot_path)
            if verbose:
                print(f"{url} = captured {'full-page' if full_page else 'minimal'} screenshot {i}/{screenshot_count}")
        return True, url
    except TimeoutException:
        if verbose:
            print(f"{url} = failed (timeout)")
        return False, url
    except WebDriverException as e:
        error_message = str(e).split('\n')[0]
        if verbose:
            print(f"{url} = failed (connection error: {error_message})")
        return False, url

def try_default_ports(url, driver, output_folder, verbose, screenshot_count, full_page):
    for port, protocol in [(80, "http"), (443, "https")]:
        full_url = f"{protocol}://{url}:{port}"
        print(f"Testing {full_url} using {protocol}...")
        success, logged_url = capture_screenshot(full_url, driver, output_folder, verbose, screenshot_count, full_page)
        if success:
            return success, logged_url
    return False, url

def generate_html_report(output_folder, success_log, fail_log):
    report_path = os.path.join(output_folder, "litewitness_report.html")
    
    with open(success_log, 'r') as success_file, open(fail_log, 'r') as fail_file:
        success_ips = [line.strip() for line in success_file.readlines()[1:] if line.strip()]
        fail_ips = [line.strip() for line in fail_file.readlines()[1:] if line.strip()]

    html_content = """
    <html>
    <head>
        <title>litewitness report</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                background-color: #1e1e1e; 
                color: #ffffff;
            }
            .container { 
                max-width: 1000px; 
                margin: 0 auto; 
                padding: 20px; 
            }
            h1 { 
                color: #ffffff; 
                text-align: center; 
            }
            .host-box { 
                background-color: #2d2d2d; 
                border: 1px solid #444; 
                margin-bottom: 20px; 
                padding: 10px; 
                border-radius: 5px; 
            }
            .host-name { 
                font-weight: bold; 
                font-size: 18px; 
                margin-bottom: 10px; 
            }
            .screenshot { 
                max-width: 980px; 
                width: 100%; 
                height: auto; 
            }
            .success { 
                color: #4caf50; 
            }
            .fail { 
                color: #f44336; 
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Litewitness Report</h1>
    """

    html_content += f'<h2 class="success">Successfully Captured ({len(success_ips)})</h2>'
    for ip in success_ips:
        screenshot_filename = next((f for f in os.listdir(output_folder) if f.startswith(ip.replace(':', '_')) and f.endswith('.png')), None)
        html_content += f"""
        <div class="host-box">
            <div class="host-name">{ip}</div>
        """
        if screenshot_filename:
            html_content += f"""
            <img class="screenshot" src="{screenshot_filename}" alt="Screenshot of {ip}">
            <p>Screenshot file: {screenshot_filename}</p>
            """
        else:
            html_content += f"""
            <p>Screenshot not found. Files in directory:</p>
            <ul>
            {"".join(f"<li>{f}</li>" for f in os.listdir(output_folder) if f.endswith('.png'))}
            </ul>
            """
        html_content += "</div>"

    # Add failed captures
    html_content += f'<h2 class="fail">Failed to Capture ({len(fail_ips)})</h2>'
    for ip in fail_ips:
        html_content += f"""
        <div class="host-box">
            <div class="host-name">{ip}</div>
            <p>Failed to capture screenshot</p>
        </div>
        """

    html_content += """
        </div>
    </body>
    </html>
    """

    with open(report_path, 'w') as report_file:
        report_file.write(html_content)

    print(f"HTML report generated at: {report_path}")

def main(input_file, xml_file, output_folder, timeout, jitter, verbose, success_log, fail_log, screenshot_count, full_page):
    driver = setup_driver(timeout)

    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder, exist_ok=True)
    except Exception as e:
        print(f"Error creating output folder: {e}")
        return

    with open(success_log, 'w') as success_file, open(fail_log, 'w') as fail_file:
        success_file.write("IP addresses successfully captured are displayed below\n")
        fail_file.write("IP addresses that were unable to be captured are displayed below\n")

    urls = parse_nmap_xml(xml_file) if xml_file else [line.strip() for line in open(input_file, 'r')]

    for url in urls:
        original_url = url
        if not url.startswith("http://") and not url.startswith("https://") and ':' not in url:
            print(f"Processing {url} on default ports 80 and 443...")
            success, logged_url = try_default_ports(url, driver, output_folder, verbose, screenshot_count, full_page)
        else:
            if ':443' in url and not url.startswith("https://"):
                url = f"https://{url.split(':')[0]}:443"
            elif ':80' in url and not url.startswith("http://"):
                url = f"http://{url.split(':')[0]}:80"

            if url.startswith("http://") or url.startswith("https://"):
                print(f"Processing {url} using {'https' if url.startswith('https') else 'http'}...")
            else:
                url = f"http://{url}"
                print(f"Processing {url} using http...")

            success, logged_url = capture_screenshot(url, driver, output_folder, verbose, screenshot_count, full_page)

        with open(success_log if success else fail_log, 'a') as log_file:
            log_file.write(f"{original_url}\n")

        if jitter:
            time.sleep(random.uniform(0, jitter))

    driver.quit()
    generate_html_report(output_folder, success_log, fail_log)

if __name__ == "__main__":
    print_banner()
    
    parser = argparse.ArgumentParser(description="litewitness: a lightweight web screenshot tool")
    parser.add_argument("-x", "--input", help="path to the input file with URLs/IPs")
    parser.add_argument("-xml", "--xmlfile", help="path to the nmap XML file")
    parser.add_argument("-o", "--output", required=True, help="output folder for screenshots and logs")
    parser.add_argument("-timeout", type=int, default=10, help="page load timeout in seconds (default: 10)")
    parser.add_argument("-ss", "--screenshotcount", type=int, default=1, help="number of screenshots per webpage (default: 1)")
    parser.add_argument("-j", "--jitter", type=float, default=0, help="jitter value to randomize delay between scans (default: 0)")
    parser.add_argument("-v", "--verbose", action="store_true", help="enable verbose output")
    parser.add_argument("-sf", "--successfile", default="success.txt", help="path to success log file (default: success.txt in output folder)")
    parser.add_argument("-ff", "--failfile", default="fail.txt", help="path to failure log file (default: fail.txt in output folder)")
    parser.add_argument("-full", "--fullpage", action="store_true", help="capture full-page screenshot, big file size! (default: off)")

    args = parser.parse_args()

    if not args.input and not args.xmlfile:
        parser.error("Either -x/--input or -xml/--xmlfile must be provided")

    success_log = args.successfile if os.path.isabs(args.successfile) else os.path.join(args.output, args.successfile)
    fail_log = args.failfile if os.path.isabs(args.failfile) else os.path.join(args.output, args.failfile)

    main(args.input, args.xmlfile, args.output, args.timeout, args.jitter, args.verbose, success_log, fail_log, args.screenshotcount, args.fullpage)
