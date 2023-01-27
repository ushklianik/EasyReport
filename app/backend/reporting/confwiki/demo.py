import requests
import json

# Set up your Confluence API credentials
base_url = 'https://easyreport.atlassian.net/wiki'
api_key = 'dmxhZG5uZW5AZ21haWwuY29tOm45YUNUdTdiNWxVVkpRMHYzblFCODNDQw=='

# Define the page title and content
title = 'First page'
content = '''
<table data-layout="default" ac:local-id="ce9dd39e-bb19-4fb3-acfb-7c4b60f15dc2">
    <colgroup>
        <col style="width: 226.67px;" />
        <col style="width: 226.67px;" />
        <col style="width: 226.67px;" />
    </colgroup>
    <tbody>
        <tr>
            <th data-highlight-colour="#b3f5ff"><p /></th>
            <th><p /></th>
            <th><p /></th>
        </tr>
        <tr>
            <td><p /></td>
            <td><p /></td>
            <td><p /></td>
        </tr>
        <tr>    
            <td><p /></td>
            <td><p /></td>
            <td><p /></td>
        </tr>
    </tbody>
</table>
<ac:image ac:align="center" ac:layout="center" ac:original-height="647" ac:original-width="1505" ac:width="680"><ri:attachment ri:filename="image-20230126-132801.png" ri:version-at-save="1" /></ac:image>
<p />
<img src="" alt="My Image"></img>
'''

# Define the parent page ID and space key
parent_id = 557057
space_key = 'MFS'

# Set up the API endpoint and headers
url = f'{base_url}/rest/api/content'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Basic {api_key}'
}
# Create the payload for the API request
payload = {
    'type': 'page',
    'title': title,
    'space': {
        'key': space_key
    },
    'ancestors': [{
        'id': parent_id
    }],
    'body': {
        'storage': {
            'value': content,
            'representation': 'storage'
        }
    }
}

# Make the API request to create the page
response = requests.post(url, headers=headers, json=payload)

# Check the response status code
if response.status_code == 201:
    print('Page created successfully')
else:
    print('Error creating page:', response.content)