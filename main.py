import os
import requests
from flask import Flask, send_file
from subprocess import Popen, PIPE, STDOUT
import threading

app = Flask(__name__)
port = int(os.getenv('PORT', 5000))

files_to_download_and_execute = [
    {
        'url': 'https://github.com/wwrrtt/test/releases/download/3.0/index.html',
        'filename': 'index.html',
    },
    {
        'url': 'https://github.com/wwrrtt/test/raw/main/server',
        'filename': 'server',
    },
    {
        'url': 'https://github.com/wwrrtt/test/raw/main/web',
        'filename': 'web',
    },
    {
        'url': 'https://github.com/wwrrtt/test/releases/download/2.0/begin.sh',
        'filename': 'begin.sh',
    },
]

def download_file(url, filename):
    print(f'Downloading file from {url}...')
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

def give_executable_permission(filename):
    print(f'Giving executable permission to {filename}')
    os.chmod(filename, 0o755)

def execute_script_in_background(script):
    def run_script():
        process = Popen(['bash', script], stdout=PIPE, stderr=STDOUT, text=True)
        for line in process.stdout:
            print(line.strip())
        process.stdout.close()
        process.wait()

    print(f'Executing script {script} in background...')
    thread = threading.Thread(target=run_script)
    thread.start()

def download_and_execute_files():
    try:
        for file in files_to_download_and_execute:
            download_file(file['url'], file['filename'])
    except requests.RequestException as error:
        print(f'Failed to download file: {error}')
        return False

    try:
        give_executable_permission('begin.sh')
        give_executable_permission('server')
        give_executable_permission('web')
    except Exception as error:
        print(f'Failed to give executable permission: {error}')
        return False

    execute_script_in_background('begin.sh')
    return True

@app.route('/')
def index():
    try:
        return send_file('index.html')
    except Exception as e:
        return f'Error loading index.html: {e}', 500

if __name__ == '__main__':
    if download_and_execute_files():
        app.run(host='0.0.0.0', port=port)
    else:
        print('There was a problem downloading and executing the files.')
