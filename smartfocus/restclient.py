# -*- coding: utf-8 -*-

"""
SmartFocus (formerly EmailVision) Campaign Commander REST Interface Client
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2013 by Mark A. Richman.
:license: GPL v2, see LICENSE for more details.

Example Usage:

from smartfocus.restclient import RESTClient

client = RESTClient(url, login, password, key)
job_id = client.insert_upload(csv)
"""

import logging
import requests

from base64 import b64encode
from poster.encode import multipart_encode, MultipartParam
from poster.streaminghttp import register_openers
from urllib import urlencode
from xml.etree import ElementTree as et
from xml.dom.minidom import parseString


class RESTClient(object):
    """ SmartFocus REST Client """
    def __init__(self, url, login, password, key):
        self.url = url
        self.open_url = url + "connect/open"
        self.close_url = url + "connect/close"
        self.login = login
        self.password = password
        self.key = key

    def insert_upload(self, csv):
        """ Uploads a file """
        credentials = urlencode({"login": self.login,
                                 "password": self.password,
                                 "key": self.key})

        # Open API session
        r = requests.get(self.open_url + "?" + credentials)
        tree = et.fromstring(r.content)
        token = tree[0].text
        logging.info("Token: " + token)

        # http://atlee.ca/software/poster/index.html
        register_openers()

        insert_upload_url = self.url + "batchmemberservice/" + token + \
            "/batchmember/insertUpload"

        # Define Column Mapping XML
        insertUpload = et.Element("insertUpload")
        criteria = et.SubElement(insertUpload, "criteria")
        criteria.text = 'LOWER(EMAIL)'
        fileName = et.SubElement(insertUpload, "fileName")
        fileName.text = 'listpull.csv'
        separator = et.SubElement(insertUpload, "separator")
        separator.text = ','
        dateFormat = et.SubElement(insertUpload, "dateFormat")
        dateFormat.text = 'MM/dd/YYYY'
        mapping = et.SubElement(insertUpload, "mapping")
        columns = {"1": "EMAIL",
                   "2": "CUSTNUM",
                   "3": "FIRSTNAME",
                   "4": "LASTNAME"}
        for k, v in sorted(columns.iteritems()):
            column = et.SubElement(mapping, "column")
            colNum = et.SubElement(column, "colNum")
            colNum.text = k
            fieldName = et.SubElement(column, "fieldName")
            fieldName.text = v
        tree = et.ElementTree(insertUpload)
        root = tree.getroot()
        data = et.tostring(root)
        logging.debug(parseString(data).toprettyxml())

        # Base64-encode CSV Data
        #try:
        #    b64data = b64encode(csv)
        #except Exception as e:
        #    logging.error("Error: " + e.message)
        #    raise

        # Construct Multipart Message
        x = [MultipartParam('insertUpload', value=data,
                            filetype="text/xml; charset=utf8"),
             MultipartParam('inputStream', value=csv, filename='email.csv',
                            filetype="application/octet-stream")]
        encData, encHeaders = multipart_encode(x)

        # Upload file
        job_id = None
        try:
            logging.info("Upload URL: " + insert_upload_url)
            upload_res = requests.put(insert_upload_url, headers=encHeaders,
                                      data=''.join(encData))
            logging.info("Status: " + str(upload_res.status_code))
            if upload_res.status_code != 200:
                logging.info("Reason: " + upload_res.reason)
            else:
                logging.info("Response: " + upload_res.text)
                tree = et.fromstring(upload_res.content)
                job_id = tree[0].text
                logging.info("Job ID: " + job_id)
        except Exception as e:
            logging.error("Error: " + e.message)
            raise

        # Close API session
        close_res = requests.get(self.close_url + "/" + token)
        logging.info("Status: " + str(close_res.status_code))
        logging.info("Response: " + close_res.text)

        return job_id