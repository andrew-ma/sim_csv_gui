import os
import shutil
import re


def main():
    APP_NAME = os.environ["APP_NAME"]
    print(f"APP_NAME: {APP_NAME}")

    TOP_LEVEL_DIR_REQUIRED_FOLDERS = ["numpy", "pandas", "smartcard", "lib"]
    TOP_LEVEL_DIR_REQUIRED_FILES = [
        f"{APP_NAME}.exe",
        "base_library.zip",
        "python39.dll",
    ]

    TOP_LEVEL_DIR_REQUIRED_EXACT = (
        TOP_LEVEL_DIR_REQUIRED_FOLDERS + TOP_LEVEL_DIR_REQUIRED_FILES
    )

    TOP_LEVEL_DIR_REQUIRED_REGEX = ["libopenblas.*.*.dll"]
    TOP_LEVEL_DIR_REQUIRED_REGEX = [
        re.compile(re_pattern) for re_pattern in TOP_LEVEL_DIR_REQUIRED_REGEX
    ]

    root_dir = os.path.join("dist", APP_NAME)
    lib_dir = os.path.join(root_dir, "lib")

    if not os.path.exists(lib_dir):
        os.makedirs(lib_dir, exist_ok=True)

    for file_or_folder in os.listdir(root_dir):
        if file_or_folder not in TOP_LEVEL_DIR_REQUIRED_EXACT:
            # and not a regex match
            for rp in TOP_LEVEL_DIR_REQUIRED_REGEX:
                if rp.match(file_or_folder):
                    break
            else:
                print(f"Move '{file_or_folder}' to lib/")
                shutil.move(os.path.join(root_dir, file_or_folder), lib_dir)


if __name__ == "__main__":
    main()
