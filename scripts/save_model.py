from ultralytics import YOLO
import torch
import os

# Carrega o modelo YOLOv8n (nano) — mais leve, rápido para testes
model = YOLO("yolov8n.pt")  # Você pode testar também "yolov8s.pt" ou outro

# Salva o modelo em formato Torch
os.makedirs("model", exist_ok=True)
torch.save(model.model, "model/model.pth")
print("Modelo salvo em model/model.pth")
