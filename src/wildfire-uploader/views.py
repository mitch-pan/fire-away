from django.shortcuts import render

from pan_cnc.lib import cnc_utils
from pan_cnc.views import CNCBaseFormView
from .uploader import submit_and_check


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

        if api_key:
            if file_name or sha256 or link:
                payload = {
                    'file_name': file_name, 'api_key': api_key, 'sha256': sha256, 'link': link }

                resp = submit_and_check(payload)

                fileName = resp['fileName']
                sha256 = resp['sha256']
                verdict = resp['verdict']
                link = resp['link']

                if link:
                    formattedResponse = f'Link: {link}\nSHA256: ' \
                                        f'{sha256}\nVerdict: {verdict}'
                else:
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