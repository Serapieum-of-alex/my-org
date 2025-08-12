CREATE TABLE repos (
    id TEXT PRIMARY KEY,
    name TEXT,
    full_name TEXT,
    private INTEGER,
    archived INTEGER,
    default_branch TEXT,
    pushed_at TEXT,
    stars INTEGER,
    forks INTEGER,
    open_issues INTEGER,
    language TEXT,
    size_kb INTEGER
);

CREATE TABLE manifests (
    repo_id TEXT,
    path TEXT,
    eco TEXT,
    commit_sha TEXT,
    PRIMARY KEY (repo_id, path)
);

CREATE TABLE dependencies (
    repo_id TEXT,
    path TEXT,
    package TEXT,
    requested TEXT,
    resolved TEXT,
    indirect INTEGER,
    license TEXT
);

CREATE TABLE vulnerabilities (
    repo_id TEXT,
    package TEXT,
    version TEXT,
    source TEXT,
    severity TEXT,
    id TEXT,
    summary TEXT
);

CREATE TABLE metrics_daily (
    repo_id TEXT,
    date TEXT,
    commits INTEGER,
    opened_prs INTEGER,
    merged_prs INTEGER,
    opened_issues INTEGER,
    closed_issues INTEGER
);
