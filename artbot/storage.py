import json


class Storage:
    def __init__(self, path="./data.json", save_on_read=False, indent=2):
        self.path = path
        self.save_on_read = save_on_read
        self.json_options = {"indent": indent}
        try:
            with open(path) as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {}

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.data, f, **self.json_options)

    def get(self, key, default=None):
        result = self.data.get(key, default)
        if self.save_on_read:
            self.set(key, result)
        return result

    def set(self, key, value):
        self.data[key] = value
        self.save()
        return value

    def has(self, key):
        return key in self.data
