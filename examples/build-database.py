# pip install PyGithub requests tomli osvc
import os, re, json, tomllib as tomli
from github import Github
import requests
from my_org.data_base.utils import SQLiteDB
from dotenv import load_dotenv
load_dotenv()

#%%
db = SQLiteDB()
# db.create_tables()

#%%
TOKEN = os.environ.get("GITHUB_TOKEN")
ORG = "Serapieum-of-alex"

github = Github(TOKEN, per_page=100)
org = github.get_organization(ORG)

#%%
for repo in org.get_repos(type="all"):
    if repo.archived: continue
    db.harvest_repo(repo)
