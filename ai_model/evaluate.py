import tensorflow as tf
from sklearn.metrics import classification_report
from .data_loader import load_dataset

if __name__ == "__main__":
    model = tf.keras.models.load_model("ai_model/saved_models/skin_lesion_cnn.h5")

    dataset_path = "dataset/processed"
    _, X_test, _, y_test, class_map = load_dataset(dataset_path)

    y_pred = model.predict(X_test)
    y_pred_classes = y_pred.argmax(axis=1)
    y_true_classes = y_test.argmax(axis=1)

    print(classification_report(y_true_classes, y_pred_classes, target_names=class_map.keys()))
