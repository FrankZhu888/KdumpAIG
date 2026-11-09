#!/usr/bin/env python3
# KdumpAIG - Automated Crash Kdump Analyzer with AI Integration
# Written by Frank Zhu <flankeroot@gmail.com>	2025-10-25

import subprocess
import sys
import os
import requests
import re
from datetime import datetime
from jinja2 import Template
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# AI API configuration
AI_API_KEY = ""
AI_API_URL = "https://openai.azure.com/openai/deployments/gpt-5-chat/chat/completions?api-version=2025-01-01-preview"
MODEL_NAME = "gpt-5-chat"

# Default output file
DEFAULT_OUTPUT_HTML = "kdump_ai_report.html"
CRASH_OUTPUT_FILE = "/tmp/crash.out"
COMMANDS_FILE = "/tmp/cmds.txt"

# Default commands if cmds.txt does not exist
DEFAULT_COMMANDS = [
    "sys", "kmem -i", "bt -a", "ps", "runq", "dev -i", "log", "irq", "swap", "timer", "sig", "net", "mach", "mod", "ipcs", "quit"
]

def print_usage():
    """Display usage instructions"""
    usage = """
Usage: # ./KdumpAIG.py --vmcore <vmcore_path> --vmlinux <vmlinux_path> [--output <output_html>]

Description:
    Analyzes a kdump vmcore file using AI (supports Azure OpenAI and DeepSeek) to
    identify potential crash causes, including system info, memory usage, backtraces, process states, run queues,
    device status, kernel logs, and more. Outputs results to an HTML report.

Required Arguments:
    --vmcore    Path to the vmcore file (e.g., /var/crash/127.0.0.1-2025-10-16-19\:15\:59/vmcore)
    --vmlinux   Path to the vmlinux file with debug symbols (e.g., /usr/lib/debug/lib/modules/$(uname -r)/vmlinux)

Optional Arguments:
    --output    Path to the output HTML report (default: kdump_ai_report.html)

Example:
    # ./KdumpAIG.py --vmcore /var/crash/127.0.0.1-2025-10-16-19\:15\:59/vmcore \\
                     --vmlinux /usr/lib/debug/lib/modules/5.14.0-503.26.1.el9_5.x86_64/vmlinux \\
                     --output report.html

Notes:
    - Requires root privileges or sudo to run crash tool.
    - Ensure crash tool is installed and available in PATH.
    - Ensure the vmcore and vmlinux files match the crashed kernel version.
    - Update AI_API_KEY, AI_API_URL and MODEL_NAME with your own AI API settings. Supported models and URL format example:
      * Azure OpenAI:   https://URI/chat/completions?api-version=2024-02-15-preview
      * DeepSeek:       https://URI/chat/completions

Support Contact: Frank Zhu <flankeroot@gmail.com>   
    """
    print(usage)

def log_progress(message, color=None):
    """Print log messages with timestamp and optional color"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if color == "red":
        print(f"\033[31m[{timestamp}] {message}\033[0m")
    elif color == "green":
        print(f"\033[32m[{timestamp}] {message}\033[0m")
    else:
        print(f"[{timestamp}] {message}")

def create_commands_file(commands_file):
    """Read crash commands from the specified file one per line, and always overwrite with defaults."""
    with open(commands_file, 'w') as f:
         for cmd in DEFAULT_COMMANDS:
             f.write(f"{cmd}\n")
    
    with open(commands_file, 'r') as f:
        commands = [line.strip() for line in f.readlines() if line.strip() and not line.startswith('#')]
    
    if not commands:
        raise Exception(f"No valid commands found in {commands_file}.")
    
    return commands

def run_crash_batch(vmcore_path, vmlinux_path):
    """Execute all crash commands from input file and write raw output to file."""
    crash_output_file = CRASH_OUTPUT_FILE
    cmds_file = COMMANDS_FILE
    timeout_seconds = 300  # 5 minutes timeout
    
    try:
        # Correct order: crash -i cmds.txt vmlinux vmcore
        # Use universal_newlines for Python 3.6 compatibility
        result = subprocess.run(
            ["crash", "-i", cmds_file, vmlinux_path, vmcore_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            timeout=timeout_seconds,
            check=True
        )
        # Write raw output without any filtering
        with open(crash_output_file, 'w') as f:
            f.write(result.stdout)
        log_progress("Kernel dump data collected successfully.")
    except subprocess.TimeoutExpired:
        log_progress(f"Crash batch execution timed out after {timeout_seconds} seconds. Output may be incomplete.", color="red")
        # Write partial output if any
        if 'result' in locals() and result.stdout:
            with open(crash_output_file, 'w') as f:
                f.write(result.stdout)
        else:
            open(crash_output_file, 'w').close()  # Ensure empty file
        raise
    except subprocess.CalledProcessError as e:
        with open(crash_output_file, 'w') as f:
            f.write(e.stdout if 'stdout' in locals() else str(e))
        log_progress(f"Crash batch execution failed: {e}", color="red")
        raise

def analyze_with_ai(crash_output_file):
    """Call AI API to analyze crash output from file"""
    if not os.path.exists(crash_output_file):
        raise Exception(f"Crash output file {crash_output_file} not found.")
    
    with open(crash_output_file, 'r') as f:
        crash_output = f.read()
    
    headers = {
        "Authorization": f"Bearer {AI_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = f"""
You are a Linux kernel expert. Below is the output from the crash tool analyzing a kdump, containing results from multiple commands:
    {crash_output}
    Please analyze and provide a preliminary conclusion, focusing on potential crash causes (e.g., deadlock, memory issues, driver errors).
Return format:
- **Problem Overview**: [Brief description of the issue]
- **Possible Causes**: [Detailed analysis of causes]
- **Recommendations**: [Suggestions for investigation or resolution]
"""
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "You are a Linux kernel expert."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": 2000,
        "temperature": 0.5,
        "top_p": 0.95
    }

    try:
        log_progress("Calling AI API for crash analysis...")
        word_count = len(crash_output.split())
        log_progress(f"Kdump trace length: {word_count} tokens")
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        response = session.post(AI_API_URL, json=payload, headers=headers, timeout=900)
        response.raise_for_status()
        data = response.json()
        if "choices" not in data or not data["choices"]:
            raise ValueError("Invalid response format from AI API")
        result = data["choices"][0]["message"]["content"].strip()
        think_match = re.search(r'<think>(.*?)</think>', result, re.DOTALL)
        think_content = think_match.group(1).strip() if think_match else "No <think> content found"
        print(f"\n{think_content}\n")
        cleaned_result = re.sub(r'<think>.*?</think>', '', result, flags=re.DOTALL).strip()
        log_progress("Kdump analysis completed successfully", color="green")
        return cleaned_result
    except requests.exceptions.RequestException as e:
        log_progress(f"AI API request failed: {e}", color="red")
        return "Analysis failed due to network or API error. Please check connectivity and API status."
    except ValueError as e:
        log_progress(f"AI API response error: {e}", color="red")
        return "Analysis failed due to invalid API response format."
    except Exception as e:
        log_progress(f"Unexpected error during AI API call: {e}", color="red")
        return "Analysis failed due to an unexpected error."

def generate_report(crash_output_file, ai_analysis, output_file):
    """Generate an HTML report with AI analysis at the top and bold headings"""
    ai_analysis_html = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', ai_analysis)
    with open(crash_output_file, 'r') as f:
        crash_outputs = f.read()
    template_str = """
<!DOCTYPE html>
<html>
<head>
    <title>Kdump AI Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1, h2 { color: #333; }
        pre { background-color: #f8f8f8; padding: 10px; white-space: pre-wrap; border: 1px solid #ddd; }
        b { font-weight: bold; }
    </style>
</head>
<body>
    <h1>Kdump AI Analysis Report</h1>
    <p>Generated on: {{ timestamp }} | Support Contact: <a href="mailto:zhuzhenquan@bytedance.com">zhuzhenquan@bytedance.com</a> ByteDance Volcano Engine Cloud Team </p>
    <h2>AI Analysis Conclusion</h2>
    <pre>{{ ai_analysis }}</pre>
    <h2>Kdump Analysis Output</h2>
    <pre>{{ crash_outputs }}</pre>
</body>
</html>
"""
    template = Template(template_str)
    html_content = template.render(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        crash_outputs=crash_outputs,
        ai_analysis=ai_analysis_html
    )
    with open(output_file, "w") as f:
        f.write(html_content)
    log_progress(f"Report generated and saved to {output_file}", color="green")

def run_default_analysis(vmcore_path, vmlinux_path, output_file=DEFAULT_OUTPUT_HTML):
    """Run commands from /tmp/cmds.txt and perform AI analysis"""
    log_progress("Initiating KdumpAIG for automated crash analysis...", color="red")
    log_progress("Processing crash dump to collect kernel data...")
    
    commands = create_commands_file(COMMANDS_FILE)
    crash_output_file = CRASH_OUTPUT_FILE
    
    # Clear output file if exists
    open(crash_output_file, 'w').close()
    
    run_crash_batch(vmcore_path, vmlinux_path)

    if not os.path.getsize(crash_output_file):
        log_progress("No valid crash output available for analysis", color="red")
        return

    ai_analysis = analyze_with_ai(crash_output_file)
    generate_report(crash_output_file, ai_analysis, output_file)
    
    # Cleanup cmds.txt after analysis
    if os.path.exists(COMMANDS_FILE):
        os.remove(COMMANDS_FILE)

    # Cleanup crash.out after analysis
    if os.path.exists(crash_output_file):
        os.remove(crash_output_file)

def main():
    """Main function to parse arguments and run default analysis"""
    if len(sys.argv) < 5 or "--vmcore" not in sys.argv or "--vmlinux" not in sys.argv:
        print_usage()
        sys.exit(1)

    vmcore_path = None
    vmlinux_path = None
    output_file = DEFAULT_OUTPUT_HTML

    # Parse arguments
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == "--vmcore" and i + 1 < len(sys.argv):
            vmcore_path = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--vmlinux" and i + 1 < len(sys.argv):
            vmlinux_path = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        else:
            print(f"Unknown or invalid argument: {sys.argv[i]}")
            print_usage()
            sys.exit(1)

    if not vmcore_path or not vmlinux_path:
        print("Error: Both --vmcore and --vmlinux arguments are required")
        print_usage()
        sys.exit(1)

    if not os.path.exists(vmcore_path) or not os.path.exists(vmlinux_path):
        log_progress("vmcore or vmlinux file does not exist, please check the paths", color="red")
        sys.exit(1)

    try:
        run_default_analysis(vmcore_path, vmlinux_path, output_file)
    except Exception as e:
        log_progress(f"Analysis failed: {e}", color="red")
        sys.exit(1)

if __name__ == "__main__":
    main()
