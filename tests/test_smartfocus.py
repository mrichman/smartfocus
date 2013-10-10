#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import httplib

from ConfigParser import SafeConfigParser
from smartfocus.restclient import RESTClient
from mom.client import SQLClient


def main():
    httplib.HTTPConnection.debuglevel = 1  # or 1
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("requests.packages.urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
    config_ini = os.path.join(os.path.dirname(__file__), 'config.ini')
    config = SafeConfigParser()
    config.read(config_ini)
    mom_host = config.get("momdb", "host")
    mom_user = config.get("momdb", "user")
    mom_password = config.get("momdb", "password")
    mom_database = config.get("momdb", "db")
    sf_url = config.get("smartfocus", "url")
    sf_login = config.get("smartfocus", "login")
    sf_password = config.get("smartfocus", "password")
    sf_key = config.get("smartfocus", "key")
    sf = RESTClient(sf_url, sf_login, sf_password, sf_key)
    mom = SQLClient(mom_host, mom_user, mom_password, mom_database)
    csv, count = mom.get_customers()
    # csv = "EMAIL,CUSTNUM,FIRSTNAME,LASTNAME\r\n" + csv
    job_id = sf.insert_upload(csv)
    print("Job ID: " + job_id)
    f = open(job_id + ".txt", "wb")
    f.write(csv)
    f.close()

if __name__ == '__main__':
    main()