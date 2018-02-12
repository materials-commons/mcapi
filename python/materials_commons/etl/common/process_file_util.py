import argparse
import sys
from materials_commons.api import get_all_projects, File, Directory


def make_project_file_id_path_table(project):
    path_table = {}
    top_dir = project.get_top_directory()
    print("Top dir: ", top_dir.name, top_dir.path)
    path = ""
    walk_dir_for_path_table(path_table, path, top_dir)
    return path_table


def walk_dir_for_path_table(path_table, path, file_or_dir):
    if type(file_or_dir) == File:
        print("File: " + file_or_dir.name)
        file_path = path + file_or_dir.name
        path_table[file_or_dir.id] = {
            'path': file_path,
            'file': file_or_dir
        }
    elif type(file_or_dir) == Directory:
        print("Directory: " + file_or_dir.name)
        dir_path = path + file_or_dir.name + "/"
        for child in file_or_dir.get_children():
            walk_dir_for_path_table(path_table, dir_path, child)
    return path_table


def test(project_name):
    project_list = get_all_projects()
    for proj in project_list:
        if proj.name == project_name:
            project = proj
    if not project:
        print("Can not find project with name = " + str(project_name) + ". Quiting.")
        return
    print("Found project: ", project.name, project.id)
    print("------")
    table = make_project_file_id_path_table(project)
    print("------")
    for key in table:
        print(key, "-->", table[key]['file'].name, table[key]['path'])


if __name__ == '__main__':
    argv = sys.argv
    parser = argparse.ArgumentParser(
        description='Build a workflow from given (well formatted) Excel spreadsheet')
    parser.add_argument('proj', type=str, help="Project Name")
    parser.add_argument('exp', type=str, help="Experiment Name")
    args = parser.parse_args(argv[1:])

    print("args: ", args.proj, args.exp)

    test(args.proj)
