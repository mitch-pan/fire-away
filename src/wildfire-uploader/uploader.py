#!/usr/bin/env python

import requests
import sys
from time import sleep

SUBMIT_URL = "https://wildfire.paloaltonetworks.com/publicapi/submit/file"
VERDICT_URL = "https://wildfire.paloaltonetworks.com/publicapi/get/verdict"
SLEEP_INTERVAL = 5

verdict_dict = {"0":"benign", "1":"malware", "2":"grayware", "-100":"pending, no verdict yet", "-101":"error", "-102":"unknown, cannot find sample record", "-103":"invalid hash"}

def submitFile(fileName, apiKey):

    try:
        files = {
            'apikey': (None, apiKey),
            'file': (fileName, open(fileName, 'rb'))
        }

        print("Sending {0} to WildFire...".format(fileName))
        response = requests.post(SUBMIT_URL, files=files)

        #print(response.text)

        if response.status_code == 200:
            start = response.text.find("<sha256>")
            real_start = len("<sha256>") + start
            end = response.text.find("</sha256>")
            sha256 = response.text[real_start:end]

        return sha256

    except IOError:
        print("Could not read/find file {0}".format(fileName))
    except requests.exceptions.ConnectionError as errc:
        print ("Error Connecting: ",errc)
    except requests.exceptions.Timeout as errt:
        print ("Timeout Error: ",errt)
    except requests.exceptions.RequestException as err:
        print ("General Connection Error: ",err)
    except OSError as err:
        print ("Error: ", err )

    return None


def getVerdict( hash, apiKey ):

    #Documentation here: https://docs.paloaltonetworks.com/wildfire/8-0/wildfire-api/get-wildfire-information-through-the-wildfire-api/get-a-wildfire-verdict-wildfire-api.html#
    verdictReceived = 0

    while verdictReceived != 1:

        try:
            files = {
                'apikey': (None, apiKey),
                'hash': (None, hash)
            }

            print("Checking verdict of hash {0}...".format(hash))
            response = requests.post(VERDICT_URL, files=files)

            #print(response.text)

            if response.status_code == 200:
                #Parse out verdict, which is an integer.  0 is benign
                start = response.text.find("<verdict>")
                real_start = len("<verdict>") + start
                end = response.text.find("</verdict>")
                verdict = response.text[real_start:end]

                #-100 means the verdict is pending, so lets ask again in two seconds
                #-102 means there is no sample, which can happen on a new submission if you ask to quickly
                if verdict != "-100":
                    verdictReceived = 1
                    v_text = verdict_dict.get(verdict)
                    print("Verdict: {0}".format(v_text))
                    return v_text
                else:
                    #Verdict was -100, so sleep and try again
                    print("Checking again in {0} seonds...".format(SLEEP_INTERVAL))
                    sleep(SLEEP_INTERVAL)

            else:
                #Something went wrong, so give up
                verdictReceived = 1

        except requests.exceptions.ConnectionError as errc:
            print ("Error Connecting: ",errc)
        except requests.exceptions.Timeout as errt:
            print ("Timeout Error: ",errt)
        except requests.exceptions.RequestException as err:
            print ("General Connection Error: ",err)
        except OSError as err:
            print ("Error: ", err )


def submit_and_check(fileNameAndKey):
    try:

        fileName = fileNameAndKey['file_name']
        apiKey = fileNameAndKey['api_key']

        sha256 = submitFile(fileName, apiKey )

        if sha256:
            print("{0} successfully submitted, sha256:{1}".format(fileName, sha256))

            sleep(2)

            #real hash
            #sha256 = "aca4b4c3dab253bfa2eb6830d7ba704c2c93ea3ec2ea59b7c15ed7952b61d957"
            #fake hash
            #sha256 = "bca4b4c3dab253bfa2eb6830d7ba704c2c93ea3ec2ea59b7c15ed7952b61d957"

            verdict_text = getVerdict(sha256, apiKey)

            print(f' "sha256": {sha256}, "verdict": {verdict_text}')

            return({ "sha256": sha256, "verdict": verdict_text })



    except IOError:
        print("Could not read file {0}".format(sys.argv[2]))


if __name__ == "__main__":
    payload = {
        'file_name': sys.argv[1], 'api_key': "f2c7a3f88dd1b65529016276a6c87cb4"}
    submit_and_check( payload )