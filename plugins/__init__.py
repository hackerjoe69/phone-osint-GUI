"""
Plugin system for extending phone intelligence capabilities
"""

class PluginBase:
    """Base class for phone intelligence plugins"""
    
    def __init__(self, name, version="1.0.0"):
        self.name = name
        self.version = version
    
    def analyze(self, phone_number, context=None):
        """
        Analyze phone number and return additional intelligence
        
        Args:
            phone_number: Parsed phone number object
            context: Additional context data
            
        Returns:
            dict: Analysis results
        """
        raise NotImplementedError("Plugin must implement analyze method")
    
    def get_info(self):
        """Return plugin information"""
        return {
            'name': self.name,
            'version': self.version,
            'description': getattr(self, 'description', 'No description available')
        }
