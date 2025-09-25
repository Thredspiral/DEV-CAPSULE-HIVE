"""
Neural Processing Engine for HybridMind

This module implements advanced neural processing capabilities including:
- Transformer-based pattern recognition
- Embedding spaces for semantic similarity
- Attention mechanisms for relevance scoring
- Multi-layer perceptron for classification
- Recurrent networks for sequential processing
- Variational autoencoders for representation learning
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
import numpy as np
from typing import Dict, List, Tuple, Any, Optional, Union
from dataclasses import dataclass
import logging
from sklearn.manifold import TSNE
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import json
from transformers import AutoModel, AutoTokenizer
import warnings

logger = logging.getLogger(__name__)


@dataclass
class NeuralPattern:
    """Represents a learned neural pattern."""
    pattern_id: str
    embedding: np.ndarray
    pattern_type: str
    confidence: float
    metadata: Dict[str, Any]
    
    def similarity(self, other: 'NeuralPattern') -> float:
        """Calculate cosine similarity with another pattern."""
        return float(cosine_similarity(
            self.embedding.reshape(1, -1), 
            other.embedding.reshape(1, -1)
        )[0, 0])


@dataclass
class ProcessingResult:
    """Result from neural processing."""
    patterns: List[NeuralPattern]
    embeddings: np.ndarray
    attention_weights: Optional[np.ndarray] = None
    classification_scores: Optional[Dict[str, float]] = None
    sequence_outputs: Optional[List[np.ndarray]] = None


class AttentionMechanism(nn.Module):
    """Multi-head attention mechanism for neural processing."""
    
    def __init__(self, d_model: int, n_heads: int = 8, dropout: float = 0.1):
        super().__init__()
        self.d_model = d_model
        self.n_heads = n_heads
        self.d_k = d_model // n_heads
        
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)
        
        self.dropout = nn.Dropout(dropout)
        self.layer_norm = nn.LayerNorm(d_model)
        
    def forward(self, query: torch.Tensor, key: torch.Tensor, 
                value: torch.Tensor, mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass of attention mechanism."""
        batch_size = query.size(0)
        seq_len = query.size(1)
        
        # Linear projections
        Q = self.W_q(query).view(batch_size, seq_len, self.n_heads, self.d_k).transpose(1, 2)
        K = self.W_k(key).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        V = self.W_v(value).view(batch_size, -1, self.n_heads, self.d_k).transpose(1, 2)
        
        # Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / np.sqrt(self.d_k)
        
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
        
        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)
        
        # Apply attention to values
        context = torch.matmul(attention_weights, V)
        context = context.transpose(1, 2).contiguous().view(
            batch_size, seq_len, self.d_model
        )
        
        # Output projection and residual connection
        output = self.W_o(context)
        output = self.layer_norm(output + query)
        
        return output, attention_weights.mean(dim=1)  # Average across heads


class TransformerEncoder(nn.Module):
    """Transformer encoder for pattern recognition."""
    
    def __init__(self, d_model: int, n_layers: int = 6, n_heads: int = 8, 
                 d_ff: int = 2048, dropout: float = 0.1):
        super().__init__()
        self.layers = nn.ModuleList([
            TransformerEncoderLayer(d_model, n_heads, d_ff, dropout)
            for _ in range(n_layers)
        ])
        
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, List[torch.Tensor]]:
        """Forward pass through encoder layers."""
        attention_weights = []
        
        for layer in self.layers:
            x, attn = layer(x, mask)
            attention_weights.append(attn)
        
        return x, attention_weights


class TransformerEncoderLayer(nn.Module):
    """Single transformer encoder layer."""
    
    def __init__(self, d_model: int, n_heads: int, d_ff: int, dropout: float = 0.1):
        super().__init__()
        self.attention = AttentionMechanism(d_model, n_heads, dropout)
        self.feed_forward = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(d_ff, d_model),
            nn.Dropout(dropout)
        )
        self.layer_norm = nn.LayerNorm(d_model)
        
    def forward(self, x: torch.Tensor, mask: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass through the layer."""
        # Self-attention
        attn_output, attn_weights = self.attention(x, x, x, mask)
        
        # Feed-forward network with residual connection
        ff_output = self.feed_forward(attn_output)
        output = self.layer_norm(ff_output + attn_output)
        
        return output, attn_weights


class VariationalAutoencoder(nn.Module):
    """Variational Autoencoder for representation learning."""
    
    def __init__(self, input_dim: int, latent_dim: int, hidden_dims: List[int] = None):
        super().__init__()
        
        if hidden_dims is None:
            hidden_dims = [512, 256, 128]
        
        self.latent_dim = latent_dim
        
        # Encoder
        encoder_layers = []
        prev_dim = input_dim
        for hidden_dim in hidden_dims:
            encoder_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.2)
            ])
            prev_dim = hidden_dim
        
        self.encoder = nn.Sequential(*encoder_layers)
        self.mu_layer = nn.Linear(hidden_dims[-1], latent_dim)
        self.logvar_layer = nn.Linear(hidden_dims[-1], latent_dim)
        
        # Decoder  
        decoder_layers = []
        prev_dim = latent_dim
        for hidden_dim in reversed(hidden_dims):
            decoder_layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.Dropout(0.2)
            ])
            prev_dim = hidden_dim
        
        decoder_layers.extend([
            nn.Linear(hidden_dims[0], input_dim),
            nn.Sigmoid()
        ])
        
        self.decoder = nn.Sequential(*decoder_layers)
    
    def encode(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """Encode input to latent space."""
        h = self.encoder(x)
        mu = self.mu_layer(h)
        logvar = self.logvar_layer(h)
        return mu, logvar
    
    def reparameterize(self, mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        """Reparameterization trick."""
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std
    
    def decode(self, z: torch.Tensor) -> torch.Tensor:
        """Decode from latent space."""
        return self.decoder(z)
    
    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Forward pass through VAE."""
        mu, logvar = self.encode(x)
        z = self.reparameterize(mu, logvar)
        recon = self.decode(z)
        return recon, mu, logvar


class RecurrentProcessor(nn.Module):
    """LSTM-based sequential processor."""
    
    def __init__(self, input_dim: int, hidden_dim: int, num_layers: int = 2,
                 dropout: float = 0.2, bidirectional: bool = True):
        super().__init__()
        
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.bidirectional = bidirectional
        
        self.lstm = nn.LSTM(
            input_dim, hidden_dim, num_layers,
            batch_first=True, dropout=dropout if num_layers > 1 else 0,
            bidirectional=bidirectional
        )
        
        self.dropout = nn.Dropout(dropout)
        
        output_dim = hidden_dim * 2 if bidirectional else hidden_dim
        self.output_projection = nn.Linear(output_dim, hidden_dim)
        
    def forward(self, x: torch.Tensor, lengths: Optional[torch.Tensor] = None) -> Tuple[torch.Tensor, torch.Tensor]:
        """Forward pass through LSTM."""
        if lengths is not None:
            # Pack sequences for variable lengths
            packed = nn.utils.rnn.pack_padded_sequence(
                x, lengths, batch_first=True, enforce_sorted=False
            )
            lstm_out, (hidden, cell) = self.lstm(packed)
            lstm_out, _ = nn.utils.rnn.pad_packed_sequence(lstm_out, batch_first=True)
        else:
            lstm_out, (hidden, cell) = self.lstm(x)
        
        # Use last hidden state
        if self.bidirectional:
            # Concatenate forward and backward final hidden states
            hidden = torch.cat([hidden[-2], hidden[-1]], dim=1)
        else:
            hidden = hidden[-1]
        
        output = self.dropout(lstm_out)
        projected = self.output_projection(output)
        
        return projected, hidden


class PatternClassifier(nn.Module):
    """Multi-layer classifier for pattern recognition."""
    
    def __init__(self, input_dim: int, num_classes: int, hidden_dims: List[int] = None,
                 dropout: float = 0.3):
        super().__init__()
        
        if hidden_dims is None:
            hidden_dims = [256, 128]
        
        layers = []
        prev_dim = input_dim
        
        for hidden_dim in hidden_dims:
            layers.extend([
                nn.Linear(prev_dim, hidden_dim),
                nn.ReLU(),
                nn.BatchNorm1d(hidden_dim),
                nn.Dropout(dropout)
            ])
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, num_classes))
        
        self.classifier = nn.Sequential(*layers)
        
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through classifier."""
        return self.classifier(x)


class EmbeddingSpace:
    """Semantic embedding space for similarity computations."""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
        except Exception as e:
            logger.warning(f"Failed to load transformer model {model_name}: {e}")
            self.tokenizer = None
            self.model = None
        
        self.embeddings_cache = {}
        self.patterns = []
        
    def encode_text(self, texts: Union[str, List[str]]) -> np.ndarray:
        """Encode text into embeddings."""
        if isinstance(texts, str):
            texts = [texts]
        
        embeddings = []
        
        for text in texts:
            if text in self.embeddings_cache:
                embeddings.append(self.embeddings_cache[text])
                continue
            
            if self.tokenizer and self.model:
                # Use transformer model
                with torch.no_grad():
                    tokens = self.tokenizer(text, return_tensors="pt", 
                                          padding=True, truncation=True, max_length=512)
                    outputs = self.model(**tokens)
                    # Use CLS token or mean pooling
                    embedding = outputs.last_hidden_state.mean(dim=1).squeeze().numpy()
            else:
                # Fallback to simple hash-based encoding
                embedding = np.random.normal(0, 1, 384)  # Random embedding as fallback
            
            self.embeddings_cache[text] = embedding
            embeddings.append(embedding)
        
        return np.array(embeddings)
    
    def find_similar(self, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[int, float]]:
        """Find most similar patterns to query."""
        if not self.patterns:
            return []
        
        pattern_embeddings = np.array([p.embedding for p in self.patterns])
        similarities = cosine_similarity(
            query_embedding.reshape(1, -1), 
            pattern_embeddings
        )[0]
        
        # Get top-k most similar
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        return [(idx, similarities[idx]) for idx in top_indices]
    
    def add_pattern(self, pattern: NeuralPattern) -> None:
        """Add pattern to the space."""
        self.patterns.append(pattern)
    
    def cluster_patterns(self, n_clusters: int = 5) -> Dict[int, List[NeuralPattern]]:
        """Cluster patterns using K-means."""
        if len(self.patterns) < n_clusters:
            return {0: self.patterns}
        
        embeddings = np.array([p.embedding for p in self.patterns])
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(embeddings)
        
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(self.patterns[i])
        
        return clusters
    
    def visualize_2d(self) -> np.ndarray:
        """Create 2D visualization of embedding space."""
        if len(self.patterns) < 2:
            return np.array([])
        
        embeddings = np.array([p.embedding for p in self.patterns])
        
        tsne = TSNE(n_components=2, random_state=42)
        return tsne.fit_transform(embeddings)


class NeuralProcessingEngine:
    """Main neural processing engine that orchestrates all neural components."""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or self._default_config()
        
        # Initialize components
        self.embedding_space = EmbeddingSpace()
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Neural models
        self.transformer = None
        self.vae = None
        self.rnn_processor = None
        self.classifier = None
        
        # Pattern storage
        self.learned_patterns = []
        self.processing_history = []
        
        logger.info(f"Neural Processing Engine initialized on device: {self.device}")
        
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for the engine."""
        return {
            'embedding_dim': 384,
            'transformer_layers': 6,
            'transformer_heads': 8,
            'hidden_dim': 256,
            'latent_dim': 64,
            'dropout': 0.1,
            'batch_size': 32,
            'learning_rate': 1e-4
        }
    
    def initialize_models(self, input_dim: int, num_classes: int = None) -> None:
        """Initialize neural models with proper dimensions."""
        config = self.config
        
        # Transformer encoder
        self.transformer = TransformerEncoder(
            d_model=config['embedding_dim'],
            n_layers=config['transformer_layers'],
            n_heads=config['transformer_heads'],
            dropout=config['dropout']
        ).to(self.device)
        
        # Variational autoencoder
        self.vae = VariationalAutoencoder(
            input_dim=input_dim,
            latent_dim=config['latent_dim']
        ).to(self.device)
        
        # Recurrent processor
        self.rnn_processor = RecurrentProcessor(
            input_dim=config['embedding_dim'],
            hidden_dim=config['hidden_dim'],
            dropout=config['dropout']
        ).to(self.device)
        
        # Pattern classifier (if num_classes provided)
        if num_classes:
            self.classifier = PatternClassifier(
                input_dim=config['embedding_dim'],
                num_classes=num_classes,
                dropout=config['dropout']
            ).to(self.device)
        
        logger.info("Neural models initialized successfully")
    
    def process_text(self, texts: Union[str, List[str]], 
                    extract_patterns: bool = True) -> ProcessingResult:
        """Process text inputs through neural pipeline."""
        if isinstance(texts, str):
            texts = [texts]
        
        # Generate embeddings
        embeddings = self.embedding_space.encode_text(texts)
        
        patterns = []
        attention_weights = None
        
        if extract_patterns and self.transformer:
            # Convert to tensor
            input_tensor = torch.FloatTensor(embeddings).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                # Process through transformer
                transformer_output, attention_weights = self.transformer(input_tensor)
                
                # Extract patterns from transformer output
                for i, text in enumerate(texts):
                    pattern_embedding = transformer_output[0, i].cpu().numpy()
                    
                    pattern = NeuralPattern(
                        pattern_id=f"text_pattern_{len(self.learned_patterns)}",
                        embedding=pattern_embedding,
                        pattern_type="text",
                        confidence=0.8,  # Default confidence
                        metadata={'text': text, 'source': 'transformer'}
                    )
                    
                    patterns.append(pattern)
                    self.learned_patterns.append(pattern)
                    self.embedding_space.add_pattern(pattern)
        
        result = ProcessingResult(
            patterns=patterns,
            embeddings=embeddings,
            attention_weights=attention_weights.cpu().numpy() if attention_weights is not None else None
        )
        
        self.processing_history.append({
            'type': 'text',
            'input_size': len(texts),
            'patterns_extracted': len(patterns)
        })
        
        return result
    
    def process_sequences(self, sequences: List[np.ndarray]) -> ProcessingResult:
        """Process sequential data through RNN."""
        if not self.rnn_processor:
            logger.warning("RNN processor not initialized")
            return ProcessingResult(patterns=[], embeddings=np.array([]))
        
        patterns = []
        
        # Convert sequences to tensors
        max_len = max(len(seq) for seq in sequences)
        padded_sequences = []
        lengths = []
        
        for seq in sequences:
            padded = np.pad(seq, ((0, max_len - len(seq)), (0, 0)), mode='constant')
            padded_sequences.append(padded)
            lengths.append(len(seq))
        
        input_tensor = torch.FloatTensor(padded_sequences).to(self.device)
        lengths_tensor = torch.LongTensor(lengths)
        
        with torch.no_grad():
            rnn_output, hidden = self.rnn_processor(input_tensor, lengths_tensor)
            
            # Extract patterns from RNN output
            for i, seq in enumerate(sequences):
                pattern_embedding = hidden[i].cpu().numpy()
                
                pattern = NeuralPattern(
                    pattern_id=f"seq_pattern_{len(self.learned_patterns)}",
                    embedding=pattern_embedding,
                    pattern_type="sequence",
                    confidence=0.7,
                    metadata={'length': len(seq), 'source': 'rnn'}
                )
                
                patterns.append(pattern)
                self.learned_patterns.append(pattern)
                self.embedding_space.add_pattern(pattern)
        
        result = ProcessingResult(
            patterns=patterns,
            embeddings=np.array([p.embedding for p in patterns]),
            sequence_outputs=[rnn_output[i, :lengths[i]].cpu().numpy() for i in range(len(sequences))]
        )
        
        return result
    
    def classify_patterns(self, patterns: List[NeuralPattern]) -> Dict[str, float]:
        """Classify patterns using trained classifier."""
        if not self.classifier:
            logger.warning("Classifier not initialized")
            return {}
        
        embeddings = np.array([p.embedding for p in patterns])
        input_tensor = torch.FloatTensor(embeddings).to(self.device)
        
        with torch.no_grad():
            logits = self.classifier(input_tensor)
            probabilities = F.softmax(logits, dim=-1)
            
            # Convert to class scores (simplified)
            class_names = [f"class_{i}" for i in range(logits.size(1))]
            scores = {}
            
            for i, class_name in enumerate(class_names):
                scores[class_name] = float(probabilities[:, i].mean())
        
        return scores
    
    def learn_representations(self, data: np.ndarray, epochs: int = 100) -> Dict[str, Any]:
        """Learn representations using VAE."""
        if not self.vae:
            logger.warning("VAE not initialized")
            return {}
        
        # Convert to tensor
        dataset = torch.FloatTensor(data)
        dataloader = DataLoader(dataset, batch_size=self.config['batch_size'], shuffle=True)
        
        optimizer = torch.optim.Adam(self.vae.parameters(), lr=self.config['learning_rate'])
        
        losses = []
        
        self.vae.train()
        for epoch in range(epochs):
            epoch_loss = 0
            
            for batch in dataloader:
                batch = batch.to(self.device)
                
                optimizer.zero_grad()
                
                recon, mu, logvar = self.vae(batch)
                
                # VAE loss (reconstruction + KL divergence)
                recon_loss = F.mse_loss(recon, batch, reduction='sum')
                kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
                loss = recon_loss + kl_loss
                
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
            
            avg_loss = epoch_loss / len(dataloader)
            losses.append(avg_loss)
            
            if epoch % 10 == 0:
                logger.debug(f"VAE Epoch {epoch}/{epochs}, Loss: {avg_loss:.4f}")
        
        self.vae.eval()
        
        # Generate sample representations
        with torch.no_grad():
            sample_data = torch.FloatTensor(data[:min(100, len(data))]).to(self.device)
            mu, logvar = self.vae.encode(sample_data)
            representations = mu.cpu().numpy()
        
        return {
            'losses': losses,
            'representations': representations,
            'latent_dim': self.config['latent_dim']
        }
    
    def find_similar_patterns(self, query: Union[str, np.ndarray], 
                             top_k: int = 5) -> List[Tuple[NeuralPattern, float]]:
        """Find patterns similar to query."""
        if isinstance(query, str):
            query_embedding = self.embedding_space.encode_text([query])[0]
        else:
            query_embedding = query
        
        similar_indices = self.embedding_space.find_similar(query_embedding, top_k)
        
        results = []
        for idx, similarity in similar_indices:
            if idx < len(self.learned_patterns):
                results.append((self.learned_patterns[idx], similarity))
        
        return results
    
    def get_attention_insights(self, text: str) -> Dict[str, Any]:
        """Get attention-based insights for text."""
        if not self.transformer:
            return {}
        
        result = self.process_text([text])
        
        insights = {
            'text': text,
            'attention_patterns': [],
            'important_tokens': []
        }
        
        if result.attention_weights is not None:
            # Analyze attention weights
            attention = result.attention_weights[0]  # First sequence
            
            # Find tokens with high attention
            avg_attention = np.mean(attention, axis=0)
            important_indices = np.argsort(avg_attention)[-5:]  # Top 5
            
            insights['attention_patterns'] = attention.tolist()
            insights['important_tokens'] = important_indices.tolist()
        
        return insights
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get engine statistics."""
        return {
            'learned_patterns': len(self.learned_patterns),
            'embedding_cache_size': len(self.embedding_space.embeddings_cache),
            'processing_history': len(self.processing_history),
            'device': str(self.device),
            'models_initialized': {
                'transformer': self.transformer is not None,
                'vae': self.vae is not None,
                'rnn': self.rnn_processor is not None,
                'classifier': self.classifier is not None
            },
            'pattern_types': self._count_pattern_types()
        }
    
    def _count_pattern_types(self) -> Dict[str, int]:
        """Count patterns by type."""
        counts = {}
        for pattern in self.learned_patterns:
            pattern_type = pattern.pattern_type
            counts[pattern_type] = counts.get(pattern_type, 0) + 1
        return counts
    
    def save_state(self, path: str) -> None:
        """Save engine state to file."""
        state = {
            'config': self.config,
            'learned_patterns': [
                {
                    'pattern_id': p.pattern_id,
                    'embedding': p.embedding.tolist(),
                    'pattern_type': p.pattern_type,
                    'confidence': p.confidence,
                    'metadata': p.metadata
                }
                for p in self.learned_patterns
            ],
            'processing_history': self.processing_history
        }
        
        with open(path, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Neural engine state saved to {path}")
    
    def load_state(self, path: str) -> None:
        """Load engine state from file."""
        with open(path, 'r') as f:
            state = json.load(f)
        
        self.config = state['config']
        
        # Reconstruct patterns
        self.learned_patterns = []
        for p_data in state['learned_patterns']:
            pattern = NeuralPattern(
                pattern_id=p_data['pattern_id'],
                embedding=np.array(p_data['embedding']),
                pattern_type=p_data['pattern_type'],
                confidence=p_data['confidence'],
                metadata=p_data['metadata']
            )
            self.learned_patterns.append(pattern)
            self.embedding_space.add_pattern(pattern)
        
        self.processing_history = state['processing_history']
        
        logger.info(f"Neural engine state loaded from {path}")


# Utility functions for neural processing

def compute_pattern_similarity_matrix(patterns: List[NeuralPattern]) -> np.ndarray:
    """Compute similarity matrix for a list of patterns."""
    n_patterns = len(patterns)
    similarity_matrix = np.zeros((n_patterns, n_patterns))
    
    for i in range(n_patterns):
        for j in range(n_patterns):
            if i != j:
                similarity_matrix[i, j] = patterns[i].similarity(patterns[j])
            else:
                similarity_matrix[i, j] = 1.0
    
    return similarity_matrix


def detect_pattern_anomalies(patterns: List[NeuralPattern], threshold: float = 0.3) -> List[NeuralPattern]:
    """Detect anomalous patterns based on similarity to others."""
    if len(patterns) < 2:
        return []
    
    similarity_matrix = compute_pattern_similarity_matrix(patterns)
    
    anomalies = []
    for i, pattern in enumerate(patterns):
        # Calculate average similarity to all other patterns
        avg_similarity = np.mean(similarity_matrix[i, :])
        
        if avg_similarity < threshold:
            anomalies.append(pattern)
    
    return anomalies


def merge_similar_patterns(patterns: List[NeuralPattern], threshold: float = 0.8) -> List[NeuralPattern]:
    """Merge very similar patterns to reduce redundancy."""
    if len(patterns) < 2:
        return patterns
    
    merged_patterns = []
    used_indices = set()
    
    for i, pattern in enumerate(patterns):
        if i in used_indices:
            continue
        
        similar_patterns = [pattern]
        used_indices.add(i)
        
        for j, other_pattern in enumerate(patterns[i+1:], i+1):
            if j in used_indices:
                continue
                
            if pattern.similarity(other_pattern) > threshold:
                similar_patterns.append(other_pattern)
                used_indices.add(j)
        
        if len(similar_patterns) > 1:
            # Merge patterns by averaging embeddings
            avg_embedding = np.mean([p.embedding for p in similar_patterns], axis=0)
            avg_confidence = np.mean([p.confidence for p in similar_patterns])
            
            merged_pattern = NeuralPattern(
                pattern_id=f"merged_{pattern.pattern_id}",
                embedding=avg_embedding,
                pattern_type=pattern.pattern_type,
                confidence=avg_confidence,
                metadata={
                    'merged_from': [p.pattern_id for p in similar_patterns],
                    'merge_count': len(similar_patterns)
                }
            )
            merged_patterns.append(merged_pattern)
        else:
            merged_patterns.append(pattern)
    
    return merged_patterns