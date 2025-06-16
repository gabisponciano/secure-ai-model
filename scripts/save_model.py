# scripts/save_model.py
import torch
import torch.nn as nn

class SimpleModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = nn.Sequential(
            nn.Linear(28*28, 128),
            nn.ReLU(),
            nn.Linear(128, 10)
        )

    def forward(self, x):
        return self.fc(x)

# Instantiate and save scripted model
model = SimpleModel()
dummy_input = torch.rand(1, 28*28)
scripted = torch.jit.trace(model, dummy_input)
scripted.save("../model/scripted_model.pt")
print("Scripted model saved.")
