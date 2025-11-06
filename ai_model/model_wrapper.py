
import pickle
import numpy as np
import os

class ModelWrapper:
    def __init__(self, model_path):
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
        else:
            from ai_model.quick_model import SimpleSkinLesionModel
            self.model = SimpleSkinLesionModel()
    
    def predict(self, image_array, filename="unknown.jpg"):
        """Predict using the simple model"""
        pred, conf = self.model.predict(filename)
        
        # Convert to format expected by the web application
        if pred == 'malignant':
            return np.array([[1-conf, conf]])  # [benign_prob, malignant_prob]
        else:
            return np.array([[conf, 1-conf]])  # [benign_prob, malignant_prob]

# Global model instance
_model = None

def get_model():
    global _model
    if _model is None:
        _model = ModelWrapper("ai_model/saved_models/skin_lesion_model.pkl")
    return _model

def predict_image(image_array, filename="unknown.jpg"):
    """Function to be called by the web application"""
    model = get_model()
    predictions = model.predict(image_array, filename)
    
    benign_prob = float(predictions[0][0])
    malignant_prob = float(predictions[0][1])
    
    if malignant_prob > benign_prob:
        return 'MALIGNANT', malignant_prob
    else:
        return 'BENIGN', benign_prob
