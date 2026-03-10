# QuantumEAR API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### Health Check
```
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "QuantumEAR",
  "version": "1.0.0",
  "timestamp": "2024-01-01T00:00:00",
  "models_loaded": true
}
```

---

### Analyze Audio (Synchronous)
```
POST /api/analyze
Content-Type: multipart/form-data
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| file | File | Yes | Audio file (.wav, .mp3, .flac, .ogg, .m4a) |

**Response (200):**
```json
{
  "id": "uuid-string",
  "filename": "sample.wav",
  "trust_score": 87.3,
  "label": "organic",
  "synthetic_probability": 0.127,
  "entropy_regions": [[1.2, 2.4], [5.1, 5.8]],
  "entropy_timeline": {
    "times": [0.0, 0.023, ...],
    "values": [0.45, 0.52, ...],
    "threshold": 0.85,
    "total_duration": 5.0
  },
  "waveform_data": [0.12, -0.34, ...],
  "spectrogram_base64": "iVBOR...",
  "processing_time_ms": 1234.5,
  "quantum_features": [0.12, -0.45, 0.78, 0.33],
  "timestamp": "2024-01-01T00:00:00",
  "status": "complete"
}
```

---

### Analyze Audio (Asynchronous)
```
POST /api/analyze/async
Content-Type: multipart/form-data
```

Returns immediately with a scan ID. Poll `/api/scan/{scan_id}/status` for progress.

**Response (200):**
```json
{
  "scan_id": "uuid-string",
  "status": "processing"
}
```

---

### Get Scan Status
```
GET /api/scan/{scan_id}/status
```

**Response:**
```json
{
  "status": "processing",
  "progress": 0.65,
  "message": "Running quantum simulation..."
}
```

---

### Get Scan Result
```
GET /api/scan/{scan_id}
```

Returns the full analysis result.

---

### Get History
```
GET /api/history?limit=50&offset=0
```

---

### Delete Scan
```
DELETE /api/history/{scan_id}
```

---

### Clear History
```
DELETE /api/history
```

## Error Responses

```json
{
  "detail": "Error message description"
}
```

| Status | Description |
|--------|-------------|
| 400 | Invalid file format or size |
| 404 | Scan not found |
| 500 | Analysis processing error |
