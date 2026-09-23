This tool was developed strictly for educational purposes, ethical footprinting, and portfolio demonstration. Users are responsible for adhering to the Terms of Service of all targeted platforms. Do not use this software to harass, stalk, or maliciously scrape user data.
# OSINT Engine 🕵️‍♂️

![Python](https://img.shields.io/badge/Python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-38B2AC?logo=tailwind-css&logoColor=white)
![Gemini AI](https://img.shields.io/badge/Gemini-3.5_Flash_Lite-8E75B2?logo=google&logoColor=white)

A high-speed, full-stack Open Source Intelligence (OSINT) web application designed to track and correlate digital footprints across the web. Built with an asynchronous Python backend, this tool sweeps 20 major platforms for target usernames and leverages Google's Gemini AI to determine the probability that disparate accounts belong to the same individual based on metadata, tech stacks, and linguistic style.

**Live Demo:** [https://osint-engine-1.onrender.com/](https://osint-engine-1.onrender.com/) *(Note: Free tier hosting may experience a 40-second cold start on the first request).*

## ✨ Features

* **Asynchronous Scanning:** Utilizes `aiohttp` to perform concurrent, non-blocking network requests, reducing a 20-platform sweep to approximately 1.5 seconds.
* **AI Identity Correlation:** Integrates `gemini-3.5-flash-lite` to dynamically read scraped bios and profile data, outputting a 0-100% confidence score on identity matches.
* **Anti-Bot Evasion:** Bypasses basic WAFs and API blocks using custom header rotation and endpoint-specific User-Agents (e.g., Reddit JSON endpoints).
* **Full-Stack Interface:** A lightweight, responsive, dark-themed frontend built with Vanilla JavaScript and Tailwind CSS.
* **Automated Dossier Generation:** Core engine is capable of exporting timestamped Markdown reports containing confirmed links and AI evidence analysis.

## 🛠️ Technology Stack

| Component | Technology |
| :--- | :--- |
| **Backend API** | FastAPI, Python |
| **Network Engine** | `aiohttp`, `asyncio` |
| **AI Integration** | Google GenAI SDK (`gemini-3.5-flash-lite`) |
| **Frontend** | HTML5, Vanilla JavaScript, Tailwind CSS |
| **Deployment** | Render (Web Services) |

## 🎯 Supported Targets
The engine currently correlates identities across 20 platforms, focusing heavily on developer and cybersecurity ecosystems:
* GitHub, HackerNews, DEV Community, PyPI, npm, DockerHub
* TryHackMe, HackTheBox, Kaggle
* Reddit, Medium, Keybase, Patreon, SoundCloud, Figma, Pastebin, Codecademy

## 🚀 Local Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/KHUSHALSY/osint_engine
