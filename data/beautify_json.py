# The purpose of this script it to increase the readability of the json files for, visual inspection, by adding line breaks and indentation.

import json
import os

def beautify_json() -> json:

    data_files = {
        "companyA": {
            "companyA/data_blocks.json",
            "companyA/family_tree.json",
        },
        "companyB": {
            "companyB/data_blocks.json",
            "companyB/family_tree.json",
        },
        "companyC": {
            "companyC/data_blocks.json",
            "companyC/family_tree.json",
        }
    }

    # Read the json files, beautify them and save them on the same location with _beautified.json suffix
    for company, files in data_files.items():
        print(f"Beautifying json files for {company}...")

        for file_path in files:
            with open(file_path, 'r') as f:
                data = json.load(f)
            beautified_file_path = file_path.replace(".json", "_beautified.json")
            with open(beautified_file_path, 'w') as f:
                json.dump(data, f, indent=4)

            # Move the original file to a backup folder
            backup_folder = os.path.join(company, "raw_json_backup")

            if not os.path.exists(backup_folder):
                os.makedirs(backup_folder)

            backup_file_path = os.path.join(backup_folder, os.path.basename(file_path))

            # Move the original file to a backup location
            os.rename(file_path, backup_file_path)

            print(f"Beautified {file_path} and moved original to {backup_file_path}")

if __name__ == "__main__":
    beautify_json()