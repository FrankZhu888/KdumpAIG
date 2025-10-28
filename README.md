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

## Example
`# ./KdumpAIG.py --vmcore /var/crash/127.0.0.1-2025-03-13-14\:50\:01/vmcore --vmlinux /usr/lib/debug/lib/modules/5.14.0-503.26.1.el9_5.x86_64/vmlinux` 

Azure OpenAI:

DeepSeek R1:


## Analysis Report
The script generates an HTML report (kdump_ai_report.html) containing detailed analysis results.

Azure OpenAI:


DeepSeek R1:



## Notes
It supports most Linux distributions and kernel versions.

Ensure the vmcore and vmlinux files match the crashed kernel version.

The script requires root privileges to install dependencies and access vmcore files.

## Support Contact

For issues or questions, contact:

Frank Zhu [flankeroot@gmail.com](mailto:flankeroot@gmail.com)  

