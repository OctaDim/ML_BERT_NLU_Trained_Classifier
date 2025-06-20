import os


def validate_dirs_file_path(full_path_file_name: str) -> bool:
    if os.path.isfile(full_path_file_name):
        print(f"File already exists: {full_path_file_name}")

        if not input("Rewrite existing file? (Y/n): ") == "Y":
            file_name = os.path.basename(full_path_file_name)
            print(f"Result: File <{file_name}> not created [XXX]\n")
            return False
        os.remove(path=full_path_file_name)

    if not os.path.exists(full_path_file_name):
        os.path.dirname(full_path_file_name)

        try:
            dir_name = os.path.dirname(full_path_file_name)
            if not os.path.exists(dir_name):
                os.makedirs(
                    name=os.path.dirname(full_path_file_name),
                    exist_ok=True)
                print(f"Directory created: {dir_name}\n")
            return True
        except Exception as error:
            print(f"Error: {error}\n")
            return False
