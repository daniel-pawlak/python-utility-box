# import libraries
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.client_credential import ClientCredential

import os
import pandas as pd
import configparser
import requests
from pathlib import Path

path = r'path\sharepoint_config.txt'

# import credentials
config = configparser.ConfigParser()
config.read(path)

username = config['Sharepoint']['username']
password = config['Sharepoint']['password']

client_id = config['Sharepoint']['client_id']
client_secret = config['Sharepoint']['client_secret']

sharepoint_url = config['Sharepoint']['sharepoint_url']
sp_relative_url = config['Sharepoint']['sp_relative_url']

def get_sharepoint_context_using_app():

    # Initialize the client credentials
    client_credentials = ClientCredential(client_id, client_secret)

    # create client context object
    ctx = ClientContext(sharepoint_url).with_credentials(client_credentials)

    return ctx

def get_sharepoint_context_using_user():

    # Initialize the client credentials
    user_credentials = UserCredential(username, password)

    # create client context object
    ctx = ClientContext(sharepoint_url).with_credentials(user_credentials)

    return ctx

def upload_to_sharepoint(file_name: str):
    """
    This function is created to upload a file to SharePoint. User gives file_name, which is path to a file which will be uploaded. 
    """

    
    # File details - created for testing
    file_content = "Hello, SharePoint!"

    # Upload a file. Provide file_content if you need to upload a real file.
    response = requests.put(sp_relative_url, data=file_content.encode())

    # Another way to upload a file
    # ctx = get_sharepoint_context_using_app()

    # target_folder = ctx.web.get_folder_by_server_relative_url(sp_relative_url)

    # with open(file_name, 'rb') as content_file:
    #     file_content = content_file.read()
    #     target_folder.upload_file(file_name, file_content).execute_query()

def download_file(sp_relative_url):
    """
    This function is created to download files from SharePoint. User gives name of the script to """
    credentials = ClientCredential(client_id, client_secret)

    ctx = ClientContext(sharepoint_url).with_credentials(credentials)
    
    # sp_relative_url is the relative url of the file in sharepoint
    file_path = Path(__file__).resolve().parents[0]

    with open(file_path, "wb") as local_file:
        file = ctx.web.get_file_by_server_relative_url(sp_relative_url)
        file.download(local_file)
        ctx.execute_query()

    print(f" Your file is downloaded here: {file_path}")

file_name = r'path\test.txt'

# Use if you want to upload a file from SharePoint
# upload_to_sharepoint(file_name)

# Use if you want to download a file from SharePoint
# download_file(sp_relative_url)