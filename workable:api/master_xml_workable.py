import requests
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler
from html_sanitizer import Sanitizer
from urllib.parse import urlparse


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            request_url = urlparse(self.requestline)
            all_companies = request_url.query.split(',')   # Get all company names from URL
            allJobsXml = ET.Element('jobs')
            for company in all_companies:
                r = requests.get(
                    f"https://apply.workable.com/api/v1/widget/accounts/{company}?details=true")
                data = r.json()
                for job in data["jobs"]:
                    jobXml = ET.SubElement(allJobsXml, 'job')
                    titleXml = ET.SubElement(jobXml, 'title')
                    titleXml.text = job["title"]
                    employerXml = ET.SubElement(allJobsXml, 'Employer Email')
                    employerXml.text = f"team+{company}@climate.careers"
                    urlXml = ET.SubElement(jobXml, 'url')
                    urlXml.text = job["url"]
                    locationXml = ET.SubElement(jobXml, 'location')
                    locationXml.text = job["city"] + ", " + job["state"] + ", " + job["country"]

                    # HTML Sanitizer
                    sanitizer = Sanitizer({
                        'tags': ('em', 'strong', 'a', 'p', 'br', 'span', 'ul', 'ol', 'li', 'h1', 'h2', 'h3', 'hr'),
                        'attributes': {"a": "href"},
                    })

                    descriptionXml = ET.SubElement(jobXml, 'description')
                    descriptionXml.text = sanitizer.sanitize(job["description"])

                    idXml = ET.SubElement(jobXml, 'id')
                    idXml.text = job["shortcode"]

            self.send_response(200)
            self.send_header('Content-type', 'text/xml')
            self.send_header(
                'Cache-Control',
                'public, immutable, no-transform, s-maxage=3600, max-age=3600'
            )
            self.end_headers()
            message = ET.tostring(allJobsXml)
            self.wfile.write(message)
            return

        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = f"<h1>Internal Error</h1><p>Sorry, there was a problem. Make sure the employer's name is " \
                "included in the URL query and/or is the correct name.</p> "
            message2 = e
            self.wfile.write(message2.encode())
            return

    def do_HEAD(self):   
        try:
            request_url = urlparse(self.requestline)
            all_companies = request_url.query.split(',')
            for company in all_companies:
                r = requests.get(
                    f"https://apply.workable.com/api/v1/widget/accounts/{company}?details=true")
                if r.status_code != 200 or r.status_code != 201:
                    self.send_response(500)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    return
            else:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                return

        except:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            return
