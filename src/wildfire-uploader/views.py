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
        file_name = workflow.get('file_name')
        api_key = workflow.get('api_key')
        sha256 = workflow.get('hash')

        payload = {
            'file_name': file_name, 'api_key': api_key, 'sha256': sha256 }

        resp = submit_and_check(payload)

        fileName = resp['fileName']
        sha256 = resp['sha256']
        verdict = resp['verdict']

        formattedResponse = f'File Name: {fileName}\nSHA256: ' \
                            f'{sha256}\nVerdict: {verdict}'

        print(f"The response is: {resp}")
        print(f"The formatted response is: {formattedResponse}")

        results = super().get_context_data()
        results['results'] = formattedResponse

        return render(self.request, 'pan_cnc/results.html', context=results)