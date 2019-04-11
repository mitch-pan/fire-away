#!/usr/bin/env python

import requests
import sys
from time import sleep
from urllib.parse import urlparse


SUBMIT_FILE_URL = "https://wildfire.paloaltonetworks.com/publicapi/submit/file"
SUBMIT_LINK_URL = "https://wildfire.paloaltonetworks.com/publicapi/submit/link"
VERDICT_URL = "https://wildfire.paloaltonetworks.com/publicapi/get/verdict"
SLEEP_INTERVAL = 5

verdictDictionary = {"0": "benign", "1": "malware", "2": "grayware", "4": "phishing", "-100": "pending, no verdict yet", "-101": "error", "-102": "unknown, cannot find sample record", "-103": "invalid hash"}

def submitFile(fileName, apiKey):

    try:
        files = {
            'apikey': (None, apiKey),
            'file': (fileName, open(fileName, 'rb'))
        }

        print("Sending {0} to WildFire...".format(fileName))
        response = requests.post(SUBMIT_FILE_URL, files=files)

        print(response.text)
        print(f'Response code = {response.status_code}')

        if response.status_code == 200:

            start = response.text.find("<sha256>")
            real_start = len("<sha256>") + start
            end = response.text.find("</sha256>")
            sha256 = response.text[real_start:end]

            print(f'Returning hash = {sha256}')
        else:
            error = response.text.find("<error>")
            if error:
                start = response.text.find("<error-message>")
                real_start = len("<error-message>") + start
                end = response.text.find("</error-message>")
                errorMessage = response.text[real_start:end]
                return f'ERROR: {errorMessage}'

            #Couldn't find specifics of error, so just return generic error response
            sha256 = "ERROR"

        return sha256

    except IOError:
        print("Could not read/find file {0}".format(fileName))
        return f'ERROR: Could not read/find file {fileName}'
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting: ",errc)
        return "ERROR: Error Connecting"
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error: ",errt)
        return "ERROR: Timeout Error"
    except requests.exceptions.RequestException as err:
        print ("General Connection Error: ",err)
        return "ERROR: General Connection Error"
    except OSError as err:
        print ("Error: ", err )
        return "ERROR: General Error"

    return None

def submitLink(link, apiKey):

    try:
        params = {
            'apikey': (None, apiKey),
            'link': (None, link)
        }

        print(f'Sending {link} to WildFire...')

        response = requests.post(SUBMIT_LINK_URL, files=params)

        print(response.text)

        if response.status_code == 200:
            start = response.text.find("<sha256>")
            real_start = len("<sha256>") + start
            end = response.text.find("</sha256>")
            sha256 = response.text[real_start:end]

        #print(f'Returning hash = {sha256}')

        return sha256

    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting: ",errc)
        return "ERROR: Error Connecting"
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error: ",errt)
        return "ERROR: Timeout Error"
    except requests.exceptions.RequestException as err:
        print ("General Connection Error: ",err)
        return "ERROR: General Connection Error"
    except OSError as err:
        print ("Error: ", err )
        return "ERROR: General Error"

    return None



def getVerdict( hash, apiKey, isLink ):

    #Documentation here: https://docs.paloaltonetworks.com/wildfire/8-0/wildfire-api/get-wildfire-information-through-the-wildfire-api/get-a-wildfire-verdict-wildfire-api.html#
    verdictReceived = 0

    while verdictReceived != 1:

        try:
            files = {
                'apikey': (None, apiKey),
                'hash': (None, hash)
            }

            print(f'Checking verdict of hash = {hash}')
            response = requests.post(VERDICT_URL, files=files)

            print(response.text)

            if response.status_code == 200:
                #Parse out verdict, which is an integer.  0 is benign
                start = response.text.find("<verdict>")
                real_start = len("<verdict>") + start
                end = response.text.find("</verdict>")
                verdict = response.text[real_start:end]

                #Verdict received
                if verdict != "-100":
                    verdictReceived = 1

                    #Special handling for link response code, since -102 means benign for links
                    if isLink and verdict == "-102":
                        verdictText = "Benign link"
                    else:
                        verdictText = verdictDictionary.get(verdict)

                    #print(f'Verdict: {verdictText}')

                    return verdictText

                #-100 means the verdict is pending, so lets ask again in SLEEP_INTERVAL seconds
                else:
                    print("Checking again in {0} seonds...".format(SLEEP_INTERVAL))
                    sleep(SLEEP_INTERVAL)

            else:
                #Something went wrong, so give up
                return "Error"

        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting: ",errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error: ",errt)
        except requests.exceptions.RequestException as err:
            print ("General Connection Error: ",err)
        except OSError as err:
            print ("Error: ", err )


def submit_and_check( thingsToCheck ):
    try:

        fileName = thingsToCheck['file_name']
        link = thingsToCheck['link']
        apiKey = thingsToCheck['api_key']
        sha256 = thingsToCheck['sha256']


        #print(f'Received file={fileName}, apiKey={apiKey} and hash={sha256} link={link}')

        if link:
            sha256 = submitLink(link, apiKey)

        if sha256 == "":
            sha256 = submitFile(fileName, apiKey )

        if sha256 is not None:

            if sha256.find("ERROR") >=0:
                return ({"fileName": fileName, "sha256": sha256, "verdict": sha256, "link": link })


            sleep(2)

            #real hash
            #sha256 = "aca4b4c3dab253bfa2eb6830d7ba704c2c93ea3ec2ea59b7c15ed7952b61d957"
            #fake hash
            #sha256 = "bca4b4c3dab253bfa2eb6830d7ba704c2c93ea3ec2ea59b7c15ed7952b61d957"
            #sha256 = "37cc186e5da897b66f0e72328b0b4942ca06685169744b9d32dd39e80d00adc1"

            if link:
                verdictTetxt = getVerdict(sha256, apiKey, True)
            else:
                verdictTetxt = getVerdict(sha256, apiKey, False)

            print(f'"sha256": {sha256}, "verdict": {verdictTetxt}')

            return({ "fileName": fileName,  "sha256": sha256, "verdict": verdictTetxt, "link": link })
        else:
            return ({"fileName": fileName, "sha256": sha256, "verdict": "Unable to get verdict"})


    except IOError:
        print("Could not read file {0}".format(sys.argv[2]))
        return ({"fileName": fileName, "sha256": "none", "verdict": "Unable to read file"})


if __name__ == "__main__":



    payload = {
        'file_name': sys.argv[2], 'api_key': sys.argv[1], 'link': "https://www.paloaltonetworks.com/", 'sha256': ""}
    submit_and_check( payload )