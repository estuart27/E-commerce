import requests
import os

SUPABASE_URL = 'https://tqcxzefejgyitlnzdncp.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRxY3h6ZWZlamd5aXRsbnpkbmNwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MjU5MTgxNzQsImV4cCI6MjA0MTQ5NDE3NH0.m09ci5J3_PHObVv3U8NY2ZeMmhCQHDzLTbmGtsecvBE'

def upload_to_supabase(file):
    url = f"{SUPABASE_URL}/storage/v1/object/bucket-name"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "multipart/form-data",
    }
    files = {'file': file}
    
    response = requests.post(url, headers=headers, files=files)
    
    if response.status_code == 200:
        return response.json().get('url')  # Retorna a URL da imagem
    else:
        return None
