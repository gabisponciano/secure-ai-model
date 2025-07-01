from ultralytics import YOLO
import torch
import os

# Load YOLOv8n (nano) model
model = YOLO("yolov8n.pt")

# Save the model in Torch format
os.makedirs("model", exist_ok=True)
torch.save(model.model, "model/model.pth")
print("Model saved to model/model.pth")
