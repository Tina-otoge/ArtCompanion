import json

class Storage:
    def __init__(self, path='./data.json', save_on_read=False):
        self.path = path
        self.save_on_read = save_on_read
        try:
            with open(path) as f:
                self.data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.data = {}

    def save(self):
        with open(self.path, 'wb') as f:
            json.dump(self.data, f)

    def get(self, key, default):
        result = self.data.get(key, default)
        if self.save_on_read:
            self.data.set(key, result)
        return result

    def set(self, key, value):
        self.data[key] = value
        self.save()
        return value
