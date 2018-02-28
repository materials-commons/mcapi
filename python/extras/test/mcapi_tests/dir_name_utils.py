
class DirNameUtils:
    def __init__(self):
        self.extra_default_dir_names = ['Literature', 'Presentations', 'Project Documents']
        self.extra_default_dir_count = len(self.extra_default_dir_names)
        self.use_extra_default_dir_names = True

    def remove_extra_defalut_dirs(self, dir_list):
        ret = []
        for dir in dir_list:
            parts = dir.name.split("/")
            if (len(parts) > 1) and (parts[1] in self.extra_default_dir_names):
                print("<--", dir.name, parts[1])
                continue
            print("++>", dir.name)
            ret.append(dir)
        return ret

    def should_check_default_dirs(self):
        return self.use_extra_default_dir_names
