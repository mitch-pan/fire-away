from django.shortcuts import render

from pan_cnc.lib import cnc_utils
from pan_cnc.views import CNCBaseFormView
from .uploader import submit_and_check

from urllib.parse import urlparse


class uploadView(CNCBaseFormView):
    # define initial dynamic form from this snippet metadata
    snippet = 'run_uploader'

    def get_snippet(self):
        return self.snippet

    # once the form has been submitted and we have all the values placed in the workflow, execute this
    def form_valid(self, form):
        workflow = self.get_workflow()

        # get the values from the user submitted form here
        link = workflow.get('link')
        file_name = workflow.get('file_name')
        #api_key = workflow.get('api_key')
        sha256 = workflow.get('hash')

        # Get API Key from env variable
        api_key = self.get_value_from_workflow('api_key')

        print(f'Using API key = {api_key}')
        formattedResponse = 'Unable to get response'

        if api_key:
            if file_name or sha256 or link:

                if link:

                    result = urlparse(link)

                    scheme = result.scheme
                    path = result.path
                    netloc = result.netloc

                    if result:
                        links = []

                        #Always put the original URL in the list
                        links.append(link)

                        #Some domains will result in netloc coming back empty, so checking here first
                        if netloc:
                            if path:
                                #Add the link with just the scheme and domain, or if not scheme, just domain
                                if scheme:
                                    links.append(f'{scheme}://{netloc}')
                                else:
                                    links.append(f'{netloc}')

                                if len(path) > 1:
                                    #Append a single / to the URL
                                    if scheme:
                                        links.append(f'{scheme}://{netloc}/')
                                    else:
                                        links.append(f'{netloc}/')
                            else:
                                #There was no path, so add the / as well
                                links.append(f'{link}/')

                        # Clear formatted response, since we have something, and start appending for each result
                        formattedResponse = ''
                        for specific_link in links:
                            payload = {
                                'file_name': file_name, 'api_key': api_key, 'sha256': sha256,
                                'link': specific_link}

                            # Submit the link, and check the result
                            resp = submit_and_check(payload)

                            verdict = resp['verdict']
                            link = resp['link']
                            sha256 = resp['sha256']

                            formattedResponse = f'{formattedResponse}Link: {link}\nSHA256: {sha256}\nVerdict: {verdict}\n\n'

                #A file hash or filename was submitted
                else:

                    payload = {
                    'file_name': file_name, 'api_key': api_key, 'sha256': sha256, 'link': link }

                    resp = submit_and_check(payload)

                    fileName = resp['fileName']
                    sha256 = resp['sha256']
                    verdict = resp['verdict']

                    #If it starts with ERROR
                    if sha256.find("ERROR") != -1:
                        formattedResponse = f'File Name: {fileName}\n{sha256}\nVerdict: {verdict}'
                    else:
                        #Create the text that will be seen by the user
                        formattedResponse = f'File Name: {fileName}\nSHA256: ' \
                                        f'{sha256}\nVerdict: {verdict}'

                #print(f"The response is: {resp}")
                print(f"The formatted response is: {formattedResponse}")

            else:
                formattedResponse = f'Please enter a link, file name, or hash to submit'
        else:
            formattedResponse = f'Please setup your WF API key as a environment variable.  The key name should be' \
                                f'"api_key" and the value should be the WF API key you want to use'

        results = super().get_context_data()
        results['results'] = formattedResponse

        return render(self.request, 'pan_cnc/results.html', context=results)