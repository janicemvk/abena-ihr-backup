"""
Mock Abena SDK for Dynamic Learning Service
"""

class AbenaSDK:
    def __init__(self, config=None):
        self.config = config or {}
        print("Mock AbenaSDK initialized for Dynamic Learning")
    
    def connect(self):
        """Mock connection method"""
        return True
    
    def get_learning_data(self):
        """Mock method to get learning data"""
        return {
            "patterns": [],
            "insights": [],
            "recommendations": []
        }
    
    def update_learning_model(self, data):
        """Mock method to update learning model"""
        return {"status": "success", "updated": True}
    
    def get_clinical_context(self):
        """Mock method to get clinical context"""
        return {
            "context": "mock_clinical_context",
            "rules": [],
            "guidelines": []
        }
    
    def get_ecdome_data(self):
        """Mock method to get eCdome data"""
        return {
            "ecdome_metrics": [],
            "patient_data": [],
            "analytics": []
        } 