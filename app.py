from flask import Flask, request, render_template, jsonify
import subprocess
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

DOMAINS_FILE = '/home/Ubuntu/subdomain-scan-nuclei/domains.txt'
STATUS_FILE = '/home/Ubuntu/subdomain-scan-nuclei/status.txt'
RESULTS_FILE = '/home/Ubuntu/subdomain-scan-nuclei/subdomains2.txt'
TAKEOVER_OUTPUT_FILE = '/home/Ubuntu/subdomain-scan-nuclei/output.txt'
TAKEOVER_STATUS_FILE = '/home/Ubuntu/subdomain-scan-nuclei/takeover_status.txt'

def read_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, 'r') as file:
            status = file.read().strip()
        return status
    return 'Idle'

def read_takeover_status():
    if os.path.exists(TAKEOVER_STATUS_FILE):
        with open(TAKEOVER_STATUS_FILE, 'r') as file:
            status = file.read().strip()
        return status
    return 'Idle'

def read_results():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r') as file:
            results = file.read().splitlines()
        return results
    return []

def read_takeover_results():
    if os.path.exists(TAKEOVER_OUTPUT_FILE):
        with open(TAKEOVER_OUTPUT_FILE, 'r') as file:
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
    takeover_status = read_takeover_status()
    takeover_results = read_takeover_results()
    return render_template('index.html', domains=domains, status=status, results=results, takeover_status=takeover_status, takeover_results=takeover_results)

@app.route('/add_domain', methods=['POST'])
def add_domain():
    try:
        domain = request.form['domain']
        with open(DOMAINS_FILE, 'a') as file:
            file.write(f"{domain}\n")
        return jsonify({"status": "Domain added", "domain": domain})
    except Exception as e:
        logging.exception("Error in /add_domain")
        return jsonify({"status": "Error", "message": str(e)}), 500

@app.route('/remove_domain', methods=['POST'])
def remove_domain():
    try:
        domain = request.form['domain']
        if os.path.exists(DOMAINS_FILE):
            with open(DOMAINS_FILE, 'r') as file:
                domains = file.read().splitlines()
            if domain in domains:
                domains.remove(domain)
                with open(DOMAINS_FILE, 'w') as file:
                    file.write("\n".join(domains) + "\n")
        return jsonify({"status": "Domain removed", "domain": domain})
    except Exception as e:
        logging.exception("Error in /remove_domain")
        return jsonify({"status": "Error", "message": str(e)}), 500

@app.route('/scan', methods=['POST'])
def scan():
    try:
        with open(STATUS_FILE, 'w') as file:
            file.write('Scan started')
        subprocess.run(['tmux', 'new-session', '-d', 'cd /home/Ubuntu/subdomain-scan-nuclei && sudo sh subdomain-finder.sh'])
        return jsonify({"status": "Scan started"})
    except Exception as e:
        logging.exception("Error in /scan")
        return jsonify({"status": "Error", "message": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    try:
        status = read_status()
        if status == 'Scan started' and os.path.exists(RESULTS_FILE):
            status = 'Scan completed'
            with open(STATUS_FILE, 'w') as file:
                file.write(status)
        results = read_results()
        return jsonify({"status": status, "data": results})
    except Exception as e:
        logging.exception("Error in /status")
        return jsonify({"status": "Error", "message": str(e)}), 500

@app.route('/takeover_scan', methods=['POST'])
def takeover_scan():
    try:
        with open(TAKEOVER_STATUS_FILE, 'w') as file:
            file.write('Takeover scan started')
        subprocess.run(['tmux', 'new-session', '-d', 'cd /home/Ubuntu/subdomain-scan-nuclei && sudo nuclei -l subdomains2.txt -t ./ -o output.txt'])
        return jsonify({"status": "Takeover scan started"})
    except Exception as e:
        logging.exception("Error in /takeover_scan")
        return jsonify({"status": "Error", "message": str(e)}), 500

@app.route('/takeover_status', methods=['GET'])
def takeover_status():
    try:
        status = read_takeover_status()
        if status == 'Takeover scan started' and os.path.exists(TAKEOVER_OUTPUT_FILE):
            status = 'Takeover scan completed'
            with open(TAKEOVER_STATUS_FILE, 'w') as file:
                file.write(status)
        results = read_takeover_results()
        return jsonify({"status": status, "data": results})
    except Exception as e:
        logging.exception("Error in /takeover_status")
        return jsonify({"status": "Error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
