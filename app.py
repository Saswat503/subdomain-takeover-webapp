from flask import Flask, request, render_template, jsonify
import subprocess
import os

app = Flask(__name__)
DOMAINS_FILE = '/home/ubuntu/subdomain-scan-nuclei/domains.txt'

@app.route('/')
def index():
    domains = []
    if os.path.exists(DOMAINS_FILE):
        with open(DOMAINS_FILE, 'r') as file:
            domains = file.read().splitlines()
    return render_template('index.html', domains=domains)

@app.route('/add_domain', methods=['POST'])
def add_domain():
    domain = request.form['domain']
    with open(DOMAINS_FILE, 'a') as file:
        file.write(f"{domain}\n")
    return jsonify({"status": "Domain added", "domain": domain})

@app.route('/scan', methods=['POST'])
def scan():
    # Start the tmux session to run the subdomain scan
    subprocess.run(['tmux', 'new-session', '-d', 'cd ~/subdomain-scan-nuclei && sudo sh subdomain-finder.sh'])
    return jsonify({"status": "Scan started"})

@app.route('/status', methods=['GET'])
def status():
    # Check if the scan is completed by looking for the subdomains2.txt file
    if os.path.exists('/home/ubuntu/subdomain-scan-nuclei/subdomains2.txt'):
        with open('/home/ubuntu/subdomain-scan-nuclei/subdomains2.txt', 'r') as file:
            data = file.read().splitlines()
        return jsonify({"status": "Scan completed", "data": data})
    else:
        return jsonify({"status": "Scan in progress"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
