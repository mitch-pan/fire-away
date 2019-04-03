# Fire-Away

Fire-Away can be used to submit files to Palo Alto Networks WildFire service.  The files are submitted via WildFire's 
API, and therefore you will need an API key to use this tool.

You may submit either a local file (by providing the full path to that file) or the SHA256 has of a file.  If the path
 to a file is provided, then the hash is ignored.  If the hash is provided, then the file path is ignored.

##Getting Started
<ol><li>Download the repo:<br>
<code>git clone https://github.com/mitch-pan/fire-away.git</code>
</ol>

<ol start="2">
<li>cd into the fire-away directory
</ol>

<ol start="3">
<li>Setup a Python 3.6 virtual environment:<br>
<code>python3.6 -m venv env<br>
source venv/bin/activate
</code>
</ol>

<ol start="4">
<li>If the cnc subfolder is empty, cd into cnc and run:<br>
<code>git submodule init<br>
git submodule update<br>
</code>
</ol>

<ol start="5">
<li>Pull down required libraries for cnc: <br>
<code>cd cnc<br>
pip install -r requirements.txt
</code>
</ol>

<ol start="6">
<li>Setup the user database:<br>
<code>./manage.py migrate<br>
./manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'password')"
</code>
</ol>

<ol start="7">
<li>Start the server: <br>
<code>./manage.py runserver 5000</code>
</ol>

<ol start="8">
<li>Connect to the server from your browswer (e.g. http://localhost:5000)
</ol>

## Support
This is a Palo Alto Networks community project.

## Authors
* Mitch Rappard - [(@mitch-pan)](https://github.com/mitch-pan)


## Support Policy
The code and templates in the repo are released under an as-is, best effort, support policy. These scripts should be seen as community supported and Palo Alto Networks will contribute our expertise as and when possible. We do not provide technical support or help in using or troubleshooting the components of the project through our normal support options such as Palo Alto Networks support teams, or ASC (Authorized Support Centers) partners and backline support options. The underlying product used (the VM-Series firewall) by the scripts or templates are still supported, but the support is only for the product functionality and not for help in deploying or using the template or script itself. Unless explicitly tagged, all projects or work posted in our GitHub repository (at https://github.com/PaloAltoNetworks) or sites other than our official Downloads page on https://support.paloaltonetworks.com are provided under the best effort policy.
