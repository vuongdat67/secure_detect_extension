# Usage Guide

## 1. Backend Setup (Python)

### Create virtual environment
```bash
python -m venv .venv
````

Activate venv:

* **Windows**

```bash
.venv\Scripts\activate
```

* **Linux / macOS**

```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run backend API

```bash
uvicorn backend.api.main:app --reload
```

---

## 2. VS Code Extension Setup (Node.js)

### Install dependencies

```bash
npm install
```

### Compile & watch extension

```bash
npm run compile
npm run watch
```

> Press **F5** to start **Extension Development Host** for debugging.

---

## 3. Run Tests

```bash
pytest
```

---

## 4. Package & Install Extension

> Make sure `vsce` is installed:

```bash
npm install -g @vscode/vsce
```

### Package extension

```bash
npx vsce package
```

### Install extension

```bash
code --install-extension securecopilot-0.1.0.vsix
```

---

## 5. Demo

🎥 Demo video:
[https://youtu.be/wWT4fWxwOhU](https://youtu.be/wWT4fWxwOhU)

## 6. Resource model

[Model folder](https://drive.google.com/file/d/1KUYjf7CJHov_03QcQ7OZX5hqmQ-BBNtS/view?usp=sharing)

---

## Notes

* This project is a **demo / proof of concept**
* Features are **not fully implemented**
* Some edge cases may not be covered

Thanks.

