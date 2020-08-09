import requests
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler
from html_sanitizer import Sanitizer
from urllib.parse import urlparse


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            request_url = urlparse(self.requestline)
            r = requests.get(
                f"https://apply.workable.com/api/v1/widget/accounts/{request_url.query.split()[0]}?details=true")
            data = r.json()
            allJobsXml = ET.Element('jobs')
            for job in data["jobs"]:
                jobXml = ET.SubElement(allJobsXml, 'job')
                titleXml = ET.SubElement(jobXml, 'title')
                titleXml.text = job["title"]
                urlXml = ET.SubElement(jobXml, 'url')
                urlXml.text = job["url"]
                locationXml = ET.SubElement(jobXml, 'location')
                locationXml.text = job["city"] + job["state"] + job["country"]

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

        except:
            requests_url = urlparse(self.requestline)
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = f"<h1>Internal Error {requests_url.query}</h1><p>Sorry, there was a problem. Make sure the employer's name is " \
                      "included in the request path.</p> "
            self.wfile.write(message.encode())
            return
