# KdumpAIG - Universal Linux Kernel Crash Analyzer with AI Integration
It's a new generation for AI agent for Linux kdump analysis, "G" stands for 'General' as it works across most Linux distributions and kernel versions.

## Overview

KdumpAIG is a Python-based tool designed to automate the analysis of Linux kernel crash dumps (kdump vmcore files) on Linux systems. By leveraging AI models (currently supporting Azure OpenAI and DeepSeek), it identifies potential crash causes such as deadlocks, memory issues, or driver errors, and generates a detailed HTML report.

The tool collects critical system data using the `crash` utility, including system info, memory usage, backtraces, process states, run queues, device statistics, kernel logs, and more. The AI then analyzes this data to provide a preliminary conclusion with actionable recommendations.

## Features

- **Quick Analysis**: With new architect it captures Linux kernel data much faster even wthin one minute. 
- **Automated Analysis**: Processes kdump vmcore files with a single command.
- **AI-Powered Insights**: Integrates with Azure OpenAI or DeepSeek for intelligent crash analysis.
- **Comprehensive Data Collection**: Uses a rich set of `crash` commands to gather system state.
- **HTML Reporting**: Outputs results in an easy-to-read HTML format.
- **Linux Compatibility**: Supports most Linux distributions and kernel versions. 

## Prerequisites
- Python 3+
- `crash` utility
- `kernel-debuginfo` (install via `debuginfo-install kernel`) or both vmcore and vmlinux were collected.  
- Root privileges for execution
- AI API, Azure OpenAI or DeepSeek

## Installation

`$ git clone https://github.com/FrankZhu888/KdumpAIG.git`

`$ cd KdumpAIG`

Edit KdumpAIG.py to update AI_API_KEY, AI_API_URL and MODEL_NAME with your credentials, example for Azure OpenAI:

`AI_API_KEY = "your-azure-openai-key"`

`AI_API_URL = "https://<your-endpoint>/openai/deployments/<deployment>/chat/completions?api-version=2024-02-15-preview"`

`MODEL_NAME = "model-name"`

## Usage
`#./KdumpAIG.py --vmcore <vmcore_path> --vmlinux <vmlinux_path> [--output <output_html>]`
<img width="1235" height="817" alt="截屏2025-10-28 12 15 02" src="https://github.com/user-attachments/assets/25aae576-9725-426e-b045-c13cf65542a0" />

## Example
`# ./KdumpAIG.py --vmcore /var/crash/127.0.0.1-2025-10-16-19\:15\:59/vmcore --vmlinux /usr/lib/debug/lib/modules/5.14.0-284.118.1.el9_2.x86_64/vmlinux` 

Azure OpenAI:
<img width="1271" height="418" alt="截屏2025-10-28 12 31 52" src="https://github.com/user-attachments/assets/7243d3d4-58fb-4e46-b7d3-bb3dd50eb953" />

DeepSeek R1:
<img width="1227" height="374" alt="截屏2025-10-28 12 25 37" src="https://github.com/user-attachments/assets/3aa3cca5-8d5d-4619-a24a-72f4ef1e4036" />


## Analysis Report
The script generates an HTML report (kdump_ai_report.html) containing detailed analysis results.

Azure OpenAI:
<img width="1840" height="1103" alt="截屏2025-10-28 13 31 53" src="https://github.com/user-attachments/assets/46d87af5-e60b-4d20-8120-ca9790547568" />


DeepSeek R1:
<img width="1840" height="1103" alt="截屏2025-10-28 12 28 02" src="https://github.com/user-attachments/assets/7b92a2ad-6c68-4473-8710-99d7857ed092" />



## Notes
It supports most Linux distributions and kernel versions.

Ensure the vmcore and vmlinux files match the crashed kernel version.

The script requires root privileges to install dependencies and access vmcore files.

## Support Contact

For issues or questions, contact:

Frank Zhu [flankeroot@gmail.com](mailto:flankeroot@gmail.com)  

