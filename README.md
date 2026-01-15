## Demo

🎥 Demo video:
[https://youtu.be/wWT4fWxwOhU](https://youtu.be/wWT4fWxwOhU)

## Resources model

# Paper code (Chinese)

- pretrain or full: [train](https://www.kaggle.com/code/datvutyn/notebook2fd53223e8) (nhưng timeout 12h) - đã có dapt, tapt, assembly

- [python](https://www.kaggle.com/code/thnhtvng/final)

- assembly: lấy từ pretrain, checkpoint để làm tiếp - [assembly](https://www.kaggle.com/code/vuongdat67/assemblyc)

- [Model folder](https://drive.google.com/file/d/1KUYjf7CJHov_03QcQ7OZX5hqmQ-BBNtS/view?usp=sharing)

- [Demo YT 1 line](https://youtu.be/4-AwYVKcXZ8)

- [Demo YT multi line](https://youtu.be/lRZLO8oVCbA)

# My improvement (English)

- [dapt](https://www.kaggle.com/datasets/thnhtvng/daptmodel/)
  
- [tapt](https://www.kaggle.com/code/thnhtvng/pretrained-model/)

- full pretrain_mode: [model fg-codebert pretrain](https://www.kaggle.com/datasets/vuongdat67/pretrain-model/) and [code](https://www.kaggle.com/code/vuongdat67/pretrained-model)
  
- [python](https://www.kaggle.com/code/datvutyn/python)
  
- [assembly](https://www.kaggle.com/code/datvutyn/assembly)
  
- [code](https://www.kaggle.com/datasets/datvutyn/codetrain/)
  
- [datasets](https://www.kaggle.com/datasets/datvutyn/exploitgen-data/)
  
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

## Notes

* This project is a **demo / proof of concept**
* Features are **not fully implemented**
* Some edge cases may not be covered

Thanks.

