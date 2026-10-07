# WordSprint

Julia Yuan's vocabulary practice site for Unit 1.

## GitHub Pages

The front end runs as a static site and falls back to browser `localStorage` when the Python API is unavailable. This makes the student learning flow and demo teacher console work on GitHub Pages, but records are local to each browser. The included `server.py` provides the shared SQLite-backed API for a full deployment on a Python host.

## Local server

```bash
python3 server.py
```

Open `http://localhost:8000`.

## GitHub Pages

Publish the `quiz-site` directory from the repository's `main` branch with GitHub Pages. The entry point is `index.html`.
