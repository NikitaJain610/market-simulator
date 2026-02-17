class PluginRegistry:
    def __init__(self):
        self.plugins = {}

    def register(self, protocol_name, plugin):
        self.plugins[protocol_name] = plugin

    def get_plugin(self, protocol_name):
        return self.plugins.get(protocol_name)
