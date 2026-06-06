<p align="center">
<img width="200" height="70" alt="Screenshot 2026-06-06 213806" src="https://github.com/user-attachments/assets/057d6a8a-d1a4-4a08-8060-b00ff2f0505f" />
</p>

# Doc2Skills CLI

A lightweight CLI tool that converts documentation pages into structured skill files for AI agents.

---

## Requirements

- Python >= 3.10
- Google Chrome browser installed

---

## Installation Via Pip

```bash
pip install doctoskills
doctoskills init  #You will be asked to enter gemini api key here 
```

---

## Usage In Any Project

```bash
doctoskills add <documentation-url> --output <output-directory>
```
## Setup — Gemini API Key

Doc2Skills uses `gemma-4-31b-it`, a free model from Google with the following limits:

- 15 requests per minute
- Unlimited tokens per minute

Get a free API key from [Google AI Studio](https://aistudio.google.com/api-keys).  
For rate limit details, see the [Gemini API docs](https://ai.google.dev/gemini-api/docs/rate-limits).

---

<p align="center">
  <video src="https://github.com/user-attachments/assets/0c98f620-b3d5-4a6f-be8b-34ad19ac42ec" width="30%" autoplay loop muted playsinline>
  </video>
</p>

### Example

```bash
doctoskills add https://www.i18next.com/overview/api --output ./skills
```

The AI will generate a name and description for the skill file based on the page content. The documentation content itself is not modified.

---

## Output Example

```
---
name: i18next-configuration-options
description: Use this skill when working with i18next configuration for init() or createInstance().
             It covers options for logging, languages, namespaces, resources, and missing keys
             functionality such as saveMissing and updateMissing.
---

# i18next Configuration Options
...
```

---

## Update API Key

```bash
doctoskills update-api-key
```

The API key is stored locally in a `config.json` file in your user config directory. It is never sent to the project maintainers. All requests go directly from your machine to Google's Gemini service.

---

## Local Development

### Install from source

```bash
git clone https://github.com/Amro-Aladghem/Doc2Skills
cd Doc2Skills/Scripts
pip install -r requirements.txt
```

### Run without pip

```bash
pip install -e .
doctoskills init
doctoskills add https://docs.example.com --output ./skills
```

---

## Dependencies

```
python >= 3.10
selenium==4.12.0
webdriver-manager==4.0.0
google-genai==0.4.0
platformdirs==3.11.0
typer==0.9.0
markdownify==0.11.6
```

---

## Privacy & Data Handling

- All processing happens locally on your machine.
- No data is collected or sent to the project maintainers.
- The only external communication is between your machine and Google's Gemini API when you provide a key and make a request. Please review [Google's privacy policy](https://policies.google.com/privacy) for details.

---

## Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit: `git commit -m "add: your feature description"`
4. Push to your branch: `git push origin feature/your-feature-name`
5. Open a Pull Request

Feel free to open an issue for bug reports, feature requests, or questions. All contributions, big or small, are appreciated!

---

Reach me: [ameraladghem@gmail.com](mailto:ameraladghem@gmail.com)
