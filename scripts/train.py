"""
QuantumEAR Training Script
============================
Trains the hybrid quantum-classical pipeline on prepared dataset.

Trains:
1. Feature Extractor reducer (512 → 4 dimensions)
2. Quantum Classifier (quantum circuit weights + post-processor)
3. VQC (variational quantum classifier)

Usage:
    python scripts/train.py
    python scripts/train.py --epochs 100 --batch-size 64
    python scripts/train.py --model all     # Train all components
    python scripts/train.py --model resnet  # Train only feature extractor
    python scripts/train.py --model quantum # Train only quantum classifier

Prerequisite:
    Run scripts/prepare_dataset.py first to create the dataset.
"""

import os
import sys
import json
import time
import argparse
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader

# Add project root
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from models.config import SAMPLE_RATE, AUDIO_DURATION, NUM_QUANTUM_FEATURES, NUM_QUBITS
from utils.spectrogram import generate_mel_spectrogram, spectrogram_to_tensor


# ─── Configuration ────────────────────────────────────────────────────────────

DATASETS_DIR = PROJECT_ROOT / "datasets"
SPLITS_DIR = DATASETS_DIR / "splits"
PROCESSED_DIR = DATASETS_DIR / "processed"
CHECKPOINTS_DIR = PROJECT_ROOT / "checkpoints"

# Training defaults
DEFAULT_EPOCHS = 50
DEFAULT_BATCH_SIZE = 32
DEFAULT_LR = 1e-3
DEFAULT_WEIGHT_DECAY = 1e-4
PATIENCE = 10  # Early stopping patience


# ─── Dataset ──────────────────────────────────────────────────────────────────

class AudioDeepfakeDataset(Dataset):
    """
    Dataset for audio deepfake detection.
    Loads processed WAV files and converts to mel-spectrogram tensors.
    """
    
    def __init__(self, csv_path: str, processed_dir: str, cache_spectrograms: bool = True):
        self.df = pd.read_csv(csv_path)
        self.processed_dir = Path(processed_dir)
        self.cache = {} if cache_spectrograms else None
        
        # Verify files exist
        valid_rows = []
        for _, row in self.df.iterrows():
            label_dir = "human" if row["label"] == "organic" else "synthetic"
            file_path = self.processed_dir / label_dir / row["filename"]
            if file_path.exists():
                valid_rows.append(row)
        
        self.df = pd.DataFrame(valid_rows)
        print(f"  Dataset loaded: {len(self.df)} samples "
              f"({len(self.df[self.df['label'] == 'organic'])} organic, "
              f"{len(self.df[self.df['label'] == 'synthetic'])} synthetic)")
    
    def __len__(self):
        return len(self.df)
    
    def __getitem__(self, idx):
        row = self.df.iloc[idx]
        label_dir = "human" if row["label"] == "organic" else "synthetic"
        file_path = self.processed_dir / label_dir / row["filename"]
        
        # Check cache
        cache_key = str(file_path)
        if self.cache is not None and cache_key in self.cache:
            spec_tensor, label = self.cache[cache_key]
            return spec_tensor, label
        
        # Load audio
        import librosa
        y, sr = librosa.load(str(file_path), sr=SAMPLE_RATE, mono=True)
        
        # Generate mel-spectrogram and convert to tensor
        mel_spec = generate_mel_spectrogram(y, sr)
        spec_tensor = spectrogram_to_tensor(mel_spec)
        spec_tensor = torch.FloatTensor(spec_tensor)
        
        # Guard against NaN/Inf from bad augmented data
        if torch.isnan(spec_tensor).any() or torch.isinf(spec_tensor).any():
            spec_tensor = torch.nan_to_num(spec_tensor, nan=0.0, posinf=1.0, neginf=-1.0)
        
        # Label: 0 = organic, 1 = synthetic
        label = torch.FloatTensor([row["label_id"]])
        
        # Cache
        if self.cache is not None:
            self.cache[cache_key] = (spec_tensor, label)
        
        return spec_tensor, label


class AudioFeaturesDataset(Dataset):
    """
    Dataset that returns pre-extracted audio features.
    Used for training the quantum classifier and VQC independently.
    """
    
    def __init__(self, features: np.ndarray, labels: np.ndarray):
        self.features = torch.FloatTensor(features)
        self.labels = torch.FloatTensor(labels)
    
    def __len__(self):
        return len(self.features)
    
    def __getitem__(self, idx):
        return self.features[idx], self.labels[idx]


# ─── Training Functions ───────────────────────────────────────────────────────

def train_feature_extractor_and_classifier(
    train_loader: DataLoader,
    val_loader: DataLoader,
    epochs: int = DEFAULT_EPOCHS,
    lr: float = DEFAULT_LR,
    device: str = "cpu"
) -> Dict:
    """
    Train the complete pipeline: ResNet Feature Extractor → Quantum Classifier.
    The ResNet backbone is frozen; only the reducer and classifier are trained.
    """
    from models.feature_extractor import FeatureExtractor
    from models.quantum_classifier import QuantumClassifier
    
    print("\n" + "=" * 60)
    print("🧠 Training Feature Extractor + Quantum Classifier")
    print("=" * 60)
    
    # Initialize models
    extractor = FeatureExtractor(num_output_features=NUM_QUANTUM_FEATURES, pretrained=True).to(device)
    classifier = QuantumClassifier(num_qubits=NUM_QUBITS).to(device)
    
    # Combine into a single model for end-to-end training
    class EndToEndModel(nn.Module):
        def __init__(self, extractor, classifier):
            super().__init__()
            self.extractor = extractor
            self.classifier = classifier
        
        def forward(self, x):
            features = self.extractor(x)
            prediction = self.classifier(features)
            return prediction
    
    model = EndToEndModel(extractor, classifier).to(device)
    
    # Only train unfrozen parameters
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    total_params = sum(p.numel() for p in trainable_params)
    print(f"  Trainable parameters: {total_params:,}")
    
    optimizer = optim.Adam(trainable_params, lr=lr, weight_decay=DEFAULT_WEIGHT_DECAY)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    criterion = nn.BCELoss()
    
    # Training loop
    best_val_loss = float('inf')
    best_val_acc = 0.0
    patience_counter = 0
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    
    for epoch in range(epochs):
        # ── Train ──
        model.train()
        train_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for batch_idx, (spectrograms, labels) in enumerate(train_loader):
            spectrograms = spectrograms.to(device)
            labels = labels.to(device)
            
            optimizer.zero_grad()
            predictions = model(spectrograms)
            predictions = predictions.clamp(0.001, 0.999)  # Prevent BCELoss NaN
            loss = criterion(predictions, labels)
            if torch.isnan(loss):
                continue  # skip bad batch
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item() * spectrograms.size(0)
            predicted_labels = (predictions > 0.5).float()
            train_correct += (predicted_labels == labels).sum().item()
            train_total += labels.size(0)
            
            if (batch_idx + 1) % 10 == 0:
                print(f"    Batch [{batch_idx+1}/{len(train_loader)}] Loss: {loss.item():.4f}")
        
        train_loss /= train_total
        train_acc = train_correct / train_total * 100
        
        # ── Validate ──
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for spectrograms, labels in val_loader:
                spectrograms = spectrograms.to(device)
                labels = labels.to(device)
                
                predictions = model(spectrograms)
                predictions = predictions.clamp(0.001, 0.999)
                loss = criterion(predictions, labels)
                if torch.isnan(loss):
                    continue
                
                val_loss += loss.item() * spectrograms.size(0)
                predicted_labels = (predictions > 0.5).float()
                val_correct += (predicted_labels == labels).sum().item()
                val_total += labels.size(0)
        
        val_loss /= val_total
        val_acc = val_correct / val_total * 100
        
        scheduler.step()
        
        # Log
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(train_acc)
        history["val_acc"].append(val_acc)
        
        print(f"  Epoch [{epoch+1}/{epochs}] "
              f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.1f}% | "
              f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.1f}%")
        
        # Early stopping + checkpoint
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_val_acc = val_acc
            patience_counter = 0
            
            # Save best model
            CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)
            torch.save({
                'epoch': epoch,
                'extractor_state_dict': extractor.state_dict(),
                'classifier_state_dict': classifier.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_loss': val_loss,
                'val_acc': val_acc,
            }, CHECKPOINTS_DIR / "best_model.pt")
            print(f"  💾 Saved best model (val_acc: {val_acc:.1f}%)")
        else:
            patience_counter += 1
            if patience_counter >= PATIENCE:
                print(f"  ⏹  Early stopping at epoch {epoch+1} (patience={PATIENCE})")
                break
    
    print(f"\n  ✅ Training complete. Best val accuracy: {best_val_acc:.1f}%")
    
    return {
        "best_val_loss": best_val_loss,
        "best_val_acc": best_val_acc,
        "epochs_trained": epoch + 1,
        "history": history,
    }


def evaluate_model(test_loader: DataLoader, device: str = "cpu") -> Dict:
    """
    Evaluate the trained model on the test set.
    Computes accuracy, precision, recall, F1, and per-class metrics.
    """
    from models.feature_extractor import FeatureExtractor
    from models.quantum_classifier import QuantumClassifier
    
    print("\n" + "=" * 60)
    print("📊 Evaluating on Test Set")
    print("=" * 60)
    
    # Load best model
    checkpoint_path = CHECKPOINTS_DIR / "best_model.pt"
    if not checkpoint_path.exists():
        print("  ❌ No checkpoint found. Train the model first.")
        return {}
    
    checkpoint = torch.load(checkpoint_path, map_location=device)
    
    extractor = FeatureExtractor(num_output_features=NUM_QUANTUM_FEATURES, pretrained=True).to(device)
    classifier = QuantumClassifier(num_qubits=NUM_QUBITS).to(device)
    
    extractor.load_state_dict(checkpoint['extractor_state_dict'])
    classifier.load_state_dict(checkpoint['classifier_state_dict'])
    
    extractor.eval()
    classifier.eval()
    
    all_predictions = []
    all_labels = []
    all_probs = []
    
    with torch.no_grad():
        for spectrograms, labels in test_loader:
            spectrograms = spectrograms.to(device)
            
            features = extractor(spectrograms)
            probs = classifier(features)
            
            predicted = (probs > 0.5).float()
            
            all_predictions.extend(predicted.cpu().numpy().flatten())
            all_labels.extend(labels.cpu().numpy().flatten())
            all_probs.extend(probs.cpu().numpy().flatten())
    
    all_predictions = np.array(all_predictions)
    all_labels = np.array(all_labels)
    all_probs = np.array(all_probs)
    
    # Metrics
    accuracy = np.mean(all_predictions == all_labels) * 100
    
    # Per-class metrics
    tp = np.sum((all_predictions == 1) & (all_labels == 1))  # True synthetic
    fp = np.sum((all_predictions == 1) & (all_labels == 0))  # False synthetic
    tn = np.sum((all_predictions == 0) & (all_labels == 0))  # True organic
    fn = np.sum((all_predictions == 0) & (all_labels == 1))  # False organic (missed AI)
    
    precision = tp / (tp + fp + 1e-10) * 100
    recall = tp / (tp + fn + 1e-10) * 100
    f1 = 2 * precision * recall / (precision + recall + 1e-10)
    
    # Equal Error Rate (EER)
    from scipy.optimize import brentq
    from scipy.interpolate import interp1d
    try:
        from sklearn.metrics import roc_curve
        fpr, tpr, thresholds = roc_curve(all_labels, all_probs)
        eer = brentq(lambda x: 1. - x - interp1d(fpr, tpr)(x), 0., 1.)
        eer_pct = eer * 100
    except Exception:
        eer_pct = -1
    
    print(f"\n  📈 Results:")
    print(f"  {'─' * 40}")
    print(f"  Accuracy:    {accuracy:.1f}%")
    print(f"  Precision:   {precision:.1f}%")
    print(f"  Recall:      {recall:.1f}%")
    print(f"  F1 Score:    {f1:.1f}%")
    print(f"  EER:         {eer_pct:.2f}%") if eer_pct >= 0 else None
    print(f"  {'─' * 40}")
    print(f"  True Positives (AI detected):      {int(tp)}")
    print(f"  True Negatives (Human confirmed):  {int(tn)}")
    print(f"  False Positives (Human flagged):    {int(fp)}")
    print(f"  False Negatives (AI missed):        {int(fn)}")
    
    results = {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "eer": eer_pct,
        "tp": int(tp),
        "fp": int(fp),
        "tn": int(tn),
        "fn": int(fn),
        "total_samples": len(all_labels),
    }
    
    # Save results
    results_path = CHECKPOINTS_DIR / "evaluation_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  💾 Results saved to {results_path}")
    
    return results


# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Train QuantumEAR deepfake detector")
    parser.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE, help="Batch size")
    parser.add_argument("--lr", type=float, default=DEFAULT_LR, help="Learning rate")
    parser.add_argument("--model", type=str, default="all", choices=["all", "resnet", "quantum"],
                        help="Which model component to train")
    parser.add_argument("--evaluate-only", action="store_true", help="Only run evaluation")
    parser.add_argument("--device", type=str, default=None, help="Device (cpu/cuda)")
    args = parser.parse_args()
    
    # Device
    if args.device:
        device = args.device
    elif torch.cuda.is_available():
        device = "cuda"
        print(f"🚀 Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = "cpu"
        print("💻 Using CPU (training will be slower)")
    
    print("\n" + "=" * 60)
    print("🔊 QuantumEAR Training Pipeline")
    print("=" * 60)
    print(f"  Epochs:     {args.epochs}")
    print(f"  Batch size: {args.batch_size}")
    print(f"  LR:         {args.lr}")
    print(f"  Device:     {device}")
    print(f"  Model:      {args.model}")
    
    # Check dataset exists
    train_csv = SPLITS_DIR / "train.csv"
    val_csv = SPLITS_DIR / "val.csv"
    test_csv = SPLITS_DIR / "test.csv"
    
    for csv_path in [train_csv, val_csv, test_csv]:
        if not csv_path.exists():
            print(f"\n❌ Dataset split not found: {csv_path}")
            print(f"   Run 'python scripts/prepare_dataset.py' first!")
            return
    
    # Create datasets
    print(f"\n📂 Loading datasets...")
    
    print(f"\n  Train set:")
    train_dataset = AudioDeepfakeDataset(str(train_csv), str(PROCESSED_DIR), cache_spectrograms=True)
    
    print(f"\n  Validation set:")
    val_dataset = AudioDeepfakeDataset(str(val_csv), str(PROCESSED_DIR), cache_spectrograms=True)
    
    print(f"\n  Test set:")
    test_dataset = AudioDeepfakeDataset(str(test_csv), str(PROCESSED_DIR), cache_spectrograms=True)
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True, 
                              num_workers=0, pin_memory=(device == "cuda"), drop_last=True)
    val_loader = DataLoader(val_dataset, batch_size=args.batch_size, shuffle=False,
                            num_workers=0, pin_memory=(device == "cuda"))
    test_loader = DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False,
                             num_workers=0, pin_memory=(device == "cuda"))
    
    if not args.evaluate_only:
        # Train
        start_time = time.time()
        
        train_results = train_feature_extractor_and_classifier(
            train_loader=train_loader,
            val_loader=val_loader,
            epochs=args.epochs,
            lr=args.lr,
            device=device,
        )
        
        training_time = time.time() - start_time
        print(f"\n⏱  Total training time: {training_time/60:.1f} minutes")
    
    # Evaluate
    eval_results = evaluate_model(test_loader, device=device)
    
    # Save final training report
    report = {
        "timestamp": datetime.now().isoformat(),
        "config": {
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "lr": args.lr,
            "device": device,
            "model": args.model,
        },
        "dataset": {
            "train_samples": len(train_dataset),
            "val_samples": len(val_dataset),
            "test_samples": len(test_dataset),
        },
        "evaluation": eval_results,
    }
    
    if not args.evaluate_only:
        report["training"] = {
            "best_val_acc": train_results["best_val_acc"],
            "best_val_loss": train_results["best_val_loss"],
            "epochs_trained": train_results["epochs_trained"],
            "training_time_minutes": training_time / 60 if 'training_time' in dir() else None,
        }
    
    report_path = CHECKPOINTS_DIR / "training_report.json"
    CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Training report saved to {report_path}")
    print(f"\n{'=' * 60}")
    print(f"✅ Done! Model checkpoint saved to {CHECKPOINTS_DIR / 'best_model.pt'}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
