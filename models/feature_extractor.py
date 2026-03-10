"""
ResNet-18 Feature Extractor
=============================
Uses a pre-trained ResNet-18 to extract high-level feature vectors
from Mel-Spectrogram images. These features are then passed to the
quantum classifier for final classification.
"""

import torch
import torch.nn as nn
import torchvision.models as models
import numpy as np
from typing import Optional

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.config import RESNET_OUTPUT_DIM, NUM_QUANTUM_FEATURES


class FeatureExtractor(nn.Module):
    """
    ResNet-18 based feature extractor that outputs a compact
    feature vector suitable for quantum encoding.
    
    Architecture:
        ResNet-18 (pretrained) → AdaptiveAvgPool → FC → Quantum Features
        
    The final FC layer reduces the 512-dim ResNet features
    to NUM_QUANTUM_FEATURES dimensions for qubit encoding.
    """
    
    def __init__(self, num_output_features: int = NUM_QUANTUM_FEATURES, pretrained: bool = True):
        super().__init__()
        
        # Load pretrained ResNet-18
        weights = models.ResNet18_Weights.DEFAULT if pretrained else None
        resnet = models.resnet18(weights=weights)
        
        # Remove the final classification layer
        # Keep everything up to the adaptive avg pool
        self.backbone = nn.Sequential(*list(resnet.children())[:-1])
        
        # Dimensionality reduction: 512 → num_output_features
        # Using a small network for better feature mapping
        self.reducer = nn.Sequential(
            nn.Flatten(),
            nn.Linear(RESNET_OUTPUT_DIM, 128),
            nn.ReLU(),
            nn.BatchNorm1d(128),
            nn.Dropout(0.3),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.BatchNorm1d(64),
            nn.Linear(64, num_output_features),
            nn.Tanh()  # Bound to [-1, 1] for quantum encoding
        )
        
        # Freeze backbone for inference (fine-tune only the reducer)
        if pretrained:
            for param in self.backbone.parameters():
                param.requires_grad = False
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Extract features from spectrogram image tensor.
        
        Args:
            x: Input tensor of shape (batch, 3, 224, 224)
        
        Returns:
            Feature tensor of shape (batch, num_output_features)
            Values bounded in [-1, 1] via Tanh activation
        """
        features = self.backbone(x)
        reduced = self.reducer(features)
        return reduced
    
    def extract_features(self, spectrogram_tensor: np.ndarray) -> np.ndarray:
        """
        Convenience method for single spectrogram inference.
        
        Args:
            spectrogram_tensor: numpy array of shape (3, 224, 224)
        
        Returns:
            Feature vector of shape (num_output_features,)
        """
        self.eval()
        device = next(self.parameters()).device
        with torch.no_grad():
            x = torch.FloatTensor(spectrogram_tensor).unsqueeze(0).to(device)
            features = self.forward(x)
            return features.squeeze(0).cpu().numpy()
    
    def get_full_features(self, spectrogram_tensor: np.ndarray) -> np.ndarray:
        """
        Extract the full 512-dim ResNet features (before reduction).
        Useful for analysis and debugging.
        """
        self.eval()
        device = next(self.parameters()).device
        with torch.no_grad():
            x = torch.FloatTensor(spectrogram_tensor).unsqueeze(0).to(device)
            features = self.backbone(x)
            return features.flatten().cpu().numpy()


# Singleton instance for reuse
_extractor_instance: Optional[FeatureExtractor] = None


import os

def get_feature_extractor() -> FeatureExtractor:
    """Get or create the singleton feature extractor, loading trained weights if available."""
    global _extractor_instance
    if _extractor_instance is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        _extractor_instance = FeatureExtractor()
        _extractor_instance.to(device)
        
        # Determine path to weights relative to the project root
        current_dir = Path(__file__).parent.parent
        ckpt_path = current_dir / "checkpoints" / "best_model.pt"
        
        if ckpt_path.exists():
            print(f"📦 Loading FeatureExtractor weights from {ckpt_path} onto {device}...")
            ckpt = torch.load(str(ckpt_path), map_location=device, weights_only=False)
            if 'extractor_state_dict' in ckpt:
                _extractor_instance.load_state_dict(ckpt['extractor_state_dict'])
        else:
            print(f"⚠️  WARNING: Could not find trained weights at {ckpt_path}! Using untrained FeatureExtractor.")
            
        _extractor_instance.eval()
    return _extractor_instance
