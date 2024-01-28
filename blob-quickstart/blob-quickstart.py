import os, uuid
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

try:
    print("Azure Blob Storage Python quickstart sample")

    # Quickstart code goes here
    account_url = "https://peisyclab2.blob.core.windows.net"
    default_credential = DefaultAzureCredential()

    blob_service_client = BlobServiceClient(account_url, credential=default_credential)

    # Create a unique name for the container
    container_name = str(uuid.uuid4())
    # Create the container
    container_client = blob_service_client.create_container(container_name)
    
   # Specify the path to your local file
    local_file_path = "/Users/choupei-hsuan/Desktop/UW MSTI/510/510_Wk2_Web Scraping/510_Lab/blob-quickstart/weather_data.csv"  # replace with your file path
    local_file_name = os.path.basename(local_file_path)

    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)

    print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

    # Upload the local file
    with open(file=local_file_path, mode="rb") as data:
        blob_client.upload_blob(data)


except Exception as ex:
    print('Exception:')
    print(ex)