from ultralytics import YOLO
import torch
import os

# Carrega o modelo YOLOv8n (nano)
model = YOLO("yolov8n.pt")

# Salva o modelo em formato Torch
os.makedirs("model", exist_ok=True)
torch.save(model.model, "model/model.pth")
print("Modelo salvo em model/model.pth")
