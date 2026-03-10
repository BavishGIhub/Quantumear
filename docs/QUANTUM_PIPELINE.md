# Quantum Pipeline Documentation

## Overview

QuantumEAR uses a hybrid quantum-classical architecture for audio deepfake detection.
The quantum layer provides enhanced feature discrimination through quantum entanglement.

## Pipeline Flow

```
Audio File → Mel-Spectrogram → ResNet-18 → Feature Reduction → ZZFeatureMap → RealAmplitudes → Classification
```

## Mathematical Foundation

### State Preparation
```
φ(x) = U_Φ(x) |0⟩^⊗n
```

Where:
- `n` = number of qubits (4 by default)
- `Φ(x)` = non-linear audio features from ResNet
- `U_Φ(x)` = ZZFeatureMap unitary operator

### ZZFeatureMap Circuit

The ZZFeatureMap encodes classical features into quantum states using:

```
U_Φ(x) = exp(i Σ_k φ_k(x) Z_k) · exp(i Σ_{j,k} φ_{j,k}(x) Z_j Z_k)
```

Where:
- `Z_k` = Pauli-Z operator on qubit k
- `φ_k(x) = x_k` (single-qubit rotation)
- `φ_{j,k}(x) = (π - x_j)(π - x_k)` (two-qubit entangling gate)

### RealAmplitudes Ansatz

The trainable variational circuit uses:
- Ry rotation gates with trainable parameters
- CNOT entangling gates in full connectivity
- 3 repetition layers (configurable)

### Measurement

The observable `Z^⊗n` is measured to produce the classification output:
```
⟨ψ(x,θ)| Z^⊗n |ψ(x,θ)⟩ → post-processing → P(synthetic)
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| NUM_QUBITS | 4 | Number of qubits |
| ZZ_REPS | 2 | ZZFeatureMap repetitions |
| ANSATZ_REPS | 3 | RealAmplitudes repetitions |
| NUM_QUANTUM_FEATURES | 4 | Features encoded into qubits |

## Fallback Mode

When Qiskit is unavailable, a classical neural network (MLP) is used as fallback.
This ensures the system remains functional without quantum simulation hardware.
