import json

# Load the file
with open("data/resumes/my_resume.json", "r") as f:
    resume = json.load(f)

# Print the result
print(f"Success! Loaded resume for {resume['name']} targeting {resume['target_role']}")