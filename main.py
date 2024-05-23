from flask import Flask, send_from_directory
import requests
import os
import subprocess
import concurrent.futures
import logging

app = Flask(__name__)
port = int(os.environ.get("PORT", 3000))

# 配置日志
log_filename = 'app.log'
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_filename),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)

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

def download_file(file_info):
    url = file_info['url']
    filename = file_info['filename']
    logger.info(f'Downloading file from {url}...')
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        logger.info(f'Successfully downloaded {filename}')
        return True
    except requests.RequestException as e:
        logger.error(f'Failed to download file {filename}: {e}')
        return False

def set_executable_permission(filename):
    try:
        subprocess.run(['chmod', '+x', filename], check=True)
        logger.info(f'Given executable permission to {filename}')
    except subprocess.CalledProcessError as e:
        logger.error(f'Failed to give executable permission to {filename}: {e}')
        return False
    return True

def execute_script(script):
    try:
        process = subprocess.run(['bash', script], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        logger.info(f'{script} output: \n{process.stdout}')
        print(f'{script} output: \n{process.stdout}')
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f'Failed to execute {script}: {e}')
        logger.error(f'Stderr: {e.stderr}')
        print(f'Failed to execute {script}: {e}')
        print(f'Stderr: {e.stderr}')
        return False

def download_and_execute_files():
    # 并行下载文件
    with concurrent.futures.ThreadPoolExecutor() as executor:
        download_results = list(executor.map(download_file, files_to_download_and_execute))
    
    if not all(download_results):
        logger.error('Failed to download one or more files.')
        return False

    # 赋予可执行权限
    executable_files = [file['filename'] for file in files_to_download_and_execute if file['filename'] in ['begin.sh', 'server', 'web']]
    for filename in executable_files:
        if not set_executable_permission(filename):
            return False

    # 执行 begin.sh 脚本
    if not execute_script('begin.sh'):
        return False

    return True

@app.route('/')
def index():
    try:
        return send_from_directory('.', 'index.html')
    except Exception as e:
        logger.error(f'Error serving index.html: {e}')
        return str(e), 500

if __name__ == '__main__':
    if download_and_execute_files():
        app.run(debug=True, host='0.0.0.0', port=port)
    else:
        logger.error('There was a problem downloading and executing the files.')
