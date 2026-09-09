from sentence_transformers import SentenceTransformer
import numpy as np


EMBEDDING_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIMENSION = 384


# Load the model once
model = SentenceTransformer(
    EMBEDDING_MODEL_NAME
)


def get_model():
    return model


def encode_text(text):
    if text is None:
        raise ValueError("Text cannot be None.")

    text = str(text).strip()

    if not text:
        raise ValueError("Cannot generate embedding for empty text.")

    embedding = model.encode(
        text,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    embedding = np.asarray(
        embedding,
        dtype=np.float32
    )

    if embedding.ndim != 1:
        raise ValueError(
            f"Invalid embedding shape: {embedding.shape}"
        )

    if embedding.shape[0] != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Expected {EMBEDDING_DIMENSION} dimensions, "
            f"got {embedding.shape[0]}"
        )

    return embedding


def encode_texts(texts):

    if texts is None:
        raise ValueError("Texts cannot be None.")

    cleaned_texts = []

    for text in texts:

        if text is None:
            continue

        text = str(text).strip()

        if text:
            cleaned_texts.append(text)

    if not cleaned_texts:
        return np.empty(
            (0, EMBEDDING_DIMENSION),
            dtype=np.float32
        )

    embeddings = model.encode(
        cleaned_texts,
        batch_size=32,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    embeddings = np.asarray(
        embeddings,
        dtype=np.float32
    )

    if embeddings.ndim == 1:
        embeddings = embeddings.reshape(1, -1)

    if embeddings.ndim != 2:
        raise ValueError(
            f"Invalid embedding shape: {embeddings.shape}"
        )

    if embeddings.shape[1] != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Expected {EMBEDDING_DIMENSION} dimensions, "
            f"got {embeddings.shape[1]}"
        )

    return embeddings


def generate_embeddings(chunks):

    if chunks is None:
        return [], np.empty(
            (0, EMBEDDING_DIMENSION),
            dtype=np.float32
        )

    texts = []

    for chunk in chunks:

        if hasattr(chunk, "page_content"):
            text = chunk.page_content.strip()
        else:
            text = str(chunk).strip()

        if text:
            texts.append(text)

    embeddings = encode_texts(texts)

    return texts, embeddings