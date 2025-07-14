import pandas as pd
import re
import subprocess

FILE = "README.md"
bigDf = pd.DataFrame()
INTERVAL = 24

def add_listings():
    #read file (simplify internship repo's readme.md)
    with open(FILE, "r", encoding="utf-8") as file:
        lines = file.readlines()

    data = [] #dataframe data
    linkset = set()

    for line in lines: #list of active roles in the file
        if line.startswith("| **[") and "</a>" in line: # Skip header and separator rows and inactive roles
            parts = line.split("|")
            #extract company. Regex extracts contents of square brackets
            company_match = re.search(r'\[([^\]]+)', parts[1])    
            company = company_match.group(1)
            role = parts[2].strip()
            
            # Extract first application link from the <a href="..."> tag
            match = re.search(r'href="(https://simplify\.jobs[^"]+)"', parts[4])
            link = match.group(1) if match else None
            if (link != None):
                data.append((company, role, link))
        

    # Create DataFrame
    df = pd.DataFrame(data, columns=["Company", "Role", "Link"])
    global bigDf
    bigDf = pd.concat([bigDf, df])
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', None)

def get_commits():
    result = subprocess.run(
        ["git", "log", "--since=2024-01-01", "--pretty=format:%H", "--", FILE],
        stdout=subprocess.PIPE,
        text=True
    )
    commits = result.stdout.strip().split("\n")
    print(commits)
    return commits[::-1]  # oldest to newest

def run_code_on_commit(commit_hash):
    subprocess.run(["git", "checkout", commit_hash], stdout=subprocess.DEVNULL)
    print(f"\n--- Commit: {commit_hash} ---\n")
    add_listings()
    

commits = get_commits()
sampled = commits[::INTERVAL]
for commit in sampled:
    run_code_on_commit(commit)

# Return to main branch
subprocess.run(["git", "checkout", "main"])

filtereddf = bigDf.drop_duplicates(subset = ['Link'])
filtereddf.reset_index(drop = True, inplace = True)
filtereddf = filtereddf.drop(columns = "index")
filtereddf
filtereddf.to_csv("2024-2025_cs_internship_archive.csv")


