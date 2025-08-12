import sqlite3
from pathlib import Path
import re, json, tomllib as tomli
from my_org import __path__

DB_PATH = Path(__path__[0]) / "my-github-org.sqlite"

class SQLiteDB:
    def __init__(self):
        self.connection = sqlite3.connect(DB_PATH)
        self.cursor = self.connection.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.commit()
        self.connection.close()

    def execute(self, *args, **kwargs):
        return self.cursor.execute(*args, **kwargs)

    def create_tables(self):
        sql_text = (Path(__path__[0])/"data_base/schema.sql").read_text()
        self.cursor.executescript(sql_text)

    def upsert_repo(self, repo):
        self.cursor.execute(
            """INSERT OR REPLACE INTO repos
            (id,name,full_name,private,archived,default_branch,pushed_at,stars,forks,open_issues,language,size_kb)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (str(repo.id), repo.name, repo.full_name, int(repo.private), int(repo.archived), repo.default_branch,
             str(repo.pushed_at), repo.stargazers_count, repo.forks_count, repo.open_issues_count, repo.language,
             repo.size))
        self.connection.commit()
        
    def get_text(self, repo, path):
        try:
            file = repo.get_contents(path)
            return file.decoded_content.decode()
        except Exception:
            return None

    def parse_python(self, repo_id, path, text):
        deps = []
        if path.endswith("requirements.txt"):
            for line in text.splitlines():
                line=line.strip()
                if not line or line.startswith("#"): continue
                m = re.split(r"[<>=!~]", line, maxsplit=1)
                pkg = m[0].strip()
                ver = line[len(pkg):].strip() or None
                deps.append((repo_id, path, pkg, ver, None, 0, None))
        elif path.endswith("pyproject.toml"):
            data = tomli.loads(text)
            reqs = []
            # poetry / PEP 621
            reqs += list((data.get("project", {}).get("dependencies") or []))
            reqs += list((data.get("tool", {}).get("poetry", {}).get("dependencies") or {}).keys())
            for r in reqs:
                if isinstance(r, str):
                    pkg = re.split(r"[<>=!~ ]", r, maxsplit=1)[0]
                    ver = r[len(pkg):].strip() or None
                else:  # dict-like
                    pkg, ver = r, None
                deps.append((repo_id, path, str(pkg), ver, None, 0, None))
        return deps

    def parse_node(self, repo_id, path, text):
        deps=[]
        data=json.loads(text)
        for section in ("dependencies","devDependencies","peerDependencies","optionalDependencies"):
            for pkg, ver in (data.get(section) or {}).items():
                deps.append((repo_id, path, pkg, ver, None, 0, None))
        return deps

    def harvest_repo(self, repo):
        repo_id = str(repo.id)
        self.upsert_repo(repo)

        # Find common manifests without cloning (fast path)
        candidates = ["requirements.txt","pyproject.toml","package.json"]
        for c in candidates:
            txt = self.get_text(repo, c)
            if not txt: continue
            self.cursor.execute(
                "INSERT OR REPLACE INTO manifests(repo_id,path,eco,commit_sha) VALUES(?,?,?,?)",
                    (repo_id, c, "python" if "pyproject" in c or "requirements" in c else "node", repo.default_branch))

            if c.endswith(("requirements.txt","pyproject.toml")):
                rows = self.parse_python(repo_id, c, txt)
            elif c.endswith("package.json"):
                rows = self.parse_node(repo_id, c, txt)
            else:
                rows = []

            self.cursor.executemany(
                """INSERT INTO dependencies(repo_id,path,package,requested,resolved,indirect,license) VALUES (?,?,?,?,?,?,?)""", rows)
            self.connection.commit()