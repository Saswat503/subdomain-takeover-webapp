from flask import Flask, request, render_template, jsonify
import subprocess
import os

app = Flask(__name__)
DOMAINS_FILE = '/home/Ubuntu/subdomain-scan-nuclei/domains.txt'
STATUS_FILE = '/home/Ubuntu/subdomain-scan-nuclei/status.txt'
RESULTS_FILE = '/home/Ubuntu/subdomain-scan-nuclei/subdomains2.txt'

def read_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as file:
            status = file.read().strip()
        return status
    return 'Idle'

def read_results():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as file:
            results = file.read().splitlines()
        return results
    return []

@app.route('/')
def index():
    domains = []
    if os.path.exists(DOMAINS_FILE):
        with open(DOMAINS_FILE, 'r') as file:
            domains = file.read().splitlines()
    status = read_status()
    results = read_results()
    return render_template('index.html', domains=domains, status=status, results=results)

@app.route('/add_domain', methods=['POST'])
def add_domain():
    domain = request.form['domain']
    with open(DOMAINS_FILE, 'a') as file:
        file.write(f"{domain}\n")
    return jsonify({"status": "Domain added", "domain": domain})

@app.route('/remove_domain', methods=['POST'])
def remove_domain():
    domain = request.form['domain']
    if os.path.exists(DOMAINS_FILE):
        with open(DOMAINS_FILE, 'r') as file:
            domains = file.read().splitlines()
        if domain in domains:
            domains.remove(domain)
            with open(DOMAINS_FILE, 'w') as file:
                file.write("\n".join(domains) + "\n")
    return jsonify({"status": "Domain removed", "domain": domain})

@app.route('/scan', methods=['POST'])
def scan():
    with open(STATUS_FILE, 'w') as file:
        file.write('Scan started')
    subprocess.run(['tmux', 'new-session', '-d', 'cd /home/Ubuntu/subdomain-scan-nuclei && sudo sh subdomain-finder.sh'])
    return jsonify({"status": "Scan started"})

@app.route('/status', methods=['GET'])
def status():
    status = read_status()
    if status == 'Scan started' and os.path.exists(RESULTS_FILE):
        status = 'Scan completed'
        with open(STATUS_FILE, 'w') as file:
            file.write(status)
    results = read_results()
    return jsonify({"status": status, "data": results})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
