"""
QuantumEAR Model Configuration
===============================
Central configuration for the hybrid quantum-classical pipeline.
"""

# Audio Processing
SAMPLE_RATE = 22050
AUDIO_DURATION = 5  # seconds — truncate/pad to this length
N_MELS = 128
N_FFT = 2048
HOP_LENGTH = 512

# ResNet Feature Extraction
RESNET_OUTPUT_DIM = 512  # ResNet-18 feature vector size
NUM_QUANTUM_FEATURES = 4  # Features to encode into qubits (4-8)

# Quantum Circuit
NUM_QUBITS = 4  # Match NUM_QUANTUM_FEATURES
ZZ_REPS = 2  # Repetitions for ZZFeatureMap
ANSATZ_REPS = 3  # Repetitions for RealAmplitudes circuit

# Classification
CLASSES = ["organic", "synthetic"]
CONFIDENCE_THRESHOLD = 0.5  # Above = synthetic, below = organic

# Spectrogram Image
SPECTROGRAM_WIDTH = 224  # ResNet input size
SPECTROGRAM_HEIGHT = 224

# Spectral Entropy
ENTROPY_WINDOW_SIZE = 1024
ENTROPY_HOP = 512
HIGH_ENTROPY_THRESHOLD = 0.65  # Lowered for better AI voice detection sensitivity

# File Upload
MAX_FILE_SIZE_MB = 100  # Increased from 50MB
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac", ".wma"}

# Supabase
SUPABASE_TABLE = "scan_history"
