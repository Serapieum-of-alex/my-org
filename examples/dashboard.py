# streamlit_app.py
import streamlit as st, pandas as pd, sqlite3
from my_org.data_base.utils import SQLiteDB

db = SQLiteDB()

conn = db.connection
repos = pd.read_sql_query("SELECT * FROM repos", conn)
deps  = pd.read_sql_query("SELECT repo_id, path, package, requested FROM dependencies", conn)
vulns = pd.read_sql_query("SELECT repo_id, package, version, severity, id FROM vulnerabilities", conn)

st.title("GitHub Org – Engineering Dashboard")

lang = st.multiselect("Languages", sorted(set(repos["language"].dropna())), [])
search = st.text_input("Filter repos by name/topic")
df = repos.copy()
if lang: df = df[df["language"].isin(lang)]
if search: df = df[df["full_name"].str.contains(search, case=False, na=False)]
st.metric("Repos", len(df)); st.metric("Stars", int(df["stars"].sum()))
st.dataframe(df[["full_name","private","archived","default_branch","pushed_at","stars","forks","open_issues","language"]])

st.subheader("Top duplicated dependencies")
dup = (deps.groupby("package")["repo_id"].nunique().sort_values(ascending=False).head(25))
st.bar_chart(dup)

st.subheader("Open vulnerabilities (by severity)")
if len(vulns):
    st.dataframe(vulns)
else:
    st.write("No vulnerabilities ingested yet.")
