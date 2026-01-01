"""
ExploitGen Utils Package
Chứa các hàm xử lý data, evaluation, canonicalization
"""
import random
import numpy as np
import torch
import pandas as pd


# ============================================================================
# SEED SETTING
# ============================================================================
def set_seed(seed: int = 42):
    """Set random seed cho reproducibility"""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


# ============================================================================
# DATA CLASSES
# ============================================================================
class Example:
    """
    Một training example
    
    Attributes:
        idx: ID của example
        source: Raw natural language input
        similarity: Template natural language (sau canonical)
        target: Target code output
    """
    def __init__(self, idx, source, similarity, target):
        self.idx = idx
        self.source = source
        self.similarity = similarity
        self.target = target


class InputFeatures:
    """
    Features sau khi tokenize, convert sang tensor-ready format
    
    Attributes:
        example_id: ID của example gốc
        source_ids: Token IDs của source
        source_mask: Attention mask của source
        similarity_ids: Token IDs của similarity (template)
        similarity_mask: Attention mask của similarity
        target_ids: Token IDs của target
        target_mask: Attention mask của target
    """
    def __init__(self, example_id, source_ids, source_mask, similarity_ids, 
                 similarity_mask, target_ids, target_mask):
        self.example_id = example_id
        self.source_ids = source_ids
        self.source_mask = source_mask
        self.similarity_ids = similarity_ids
        self.similarity_mask = similarity_mask
        self.target_ids = target_ids
        self.target_mask = target_mask


# ============================================================================
# DATA LOADING
# ============================================================================
def read_examples(filename: str, stage: str = 'stage2') -> list:
    """
    ĐỌC DATA ĐÚNG THEO STAGE!
    
    Args:
        filename: Đường dẫn đến CSV file
        stage: Loại stage training
            - 'stage1_raw': raw_nl -> raw_code (Raw Encoder)
            - 'stage1_temp': temp_nl -> temp_code (Template Encoder)  
            - 'stage2': raw_nl + temp_nl -> temp_code (Full Model)
        
    Returns:
        List[Example]: List các Example objects
    """
    examples = []
    df = pd.read_csv(filename)
    
    for idx, row in df.iterrows():
        if stage == 'stage1_raw':
            # Stage 1A: Train Raw Encoder
            examples.append(Example(
                idx=idx,
                source=str(row['raw_nl']).strip(),
                similarity=str(row['raw_nl']).strip(),  # Không dùng template
                target=str(row['raw_code']).strip()     # Target là RAW code
            ))
        elif stage == 'stage1_temp':
            # Stage 1B: Train Template Encoder
            examples.append(Example(
                idx=idx,
                source=str(row['temp_nl']).strip(),     # Template NL
                similarity=str(row['temp_nl']).strip(), # Không dùng dual
                target=str(row['temp_code']).strip()    # Target là TEMPLATE code
            ))
        else:  # stage2
            # Stage 2: Full Model với Dual Encoders
            examples.append(Example(
                idx=idx,
                source=str(row['raw_nl']).strip(),      # Raw NL (Raw Encoder)
                similarity=str(row['temp_nl']).strip(), # Template NL (Template Encoder)
                target=str(row['temp_code']).strip()    # Target là TEMPLATE code
            ))
    
    return examples


# ============================================================================
# FEATURE CONVERSION
# ============================================================================
def convert_examples_to_features(examples, tokenizer, max_source_length, 
                                 max_target_length, stage='train'):
    """
    Convert Examples thành InputFeatures (tokenized, padded)
    
    Args:
        examples: List[Example]
        tokenizer: Tokenizer object (RobertaTokenizer)
        max_source_length: Max length cho source sequence
        max_target_length: Max length cho target sequence
        stage: 'train', 'dev', hoặc 'test'
        
    Returns:
        List[InputFeatures]
    """
    features = []
    
    for example_idx, example in enumerate(examples):
        # Tokenize source (raw NL)
        source_tokens = tokenizer.tokenize(example.source)[:max_source_length - 2]
        source_tokens = [tokenizer.cls_token] + source_tokens + [tokenizer.sep_token]
        source_ids = tokenizer.convert_tokens_to_ids(source_tokens)
        source_mask = [1] * len(source_ids)
        padding_length = max_source_length - len(source_ids)
        source_ids += [tokenizer.pad_token_id] * padding_length
        source_mask += [0] * padding_length
        
        # Tokenize similarity (template NL)
        similarity_tokens = tokenizer.tokenize(example.similarity)[:max_source_length - 2]
        similarity_tokens = [tokenizer.cls_token] + similarity_tokens + [tokenizer.sep_token]
        similarity_ids = tokenizer.convert_tokens_to_ids(similarity_tokens)
        similarity_mask = [1] * len(similarity_ids)
        padding_length = max_source_length - len(similarity_ids)
        similarity_ids += [tokenizer.pad_token_id] * padding_length
        similarity_mask += [0] * padding_length
        
        # Tokenize target (template code)
        if stage == 'test':
            # FIX: Test stage cần padding đúng độ dài
            target_ids = [tokenizer.pad_token_id] * max_target_length
            target_mask = [0] * max_target_length
        else:
            target_tokens = tokenizer.tokenize(example.target)[:max_target_length - 2]
            target_tokens = [tokenizer.cls_token] + target_tokens + [tokenizer.sep_token]
            target_ids = tokenizer.convert_tokens_to_ids(target_tokens)
            target_mask = [1] * len(target_ids)
            padding_length = max_target_length - len(target_ids)
            target_ids += [tokenizer.pad_token_id] * padding_length
            target_mask += [0] * padding_length
        
        # Validation
        assert len(source_ids) == max_source_length, \
            f"Source IDs length mismatch: {len(source_ids)} vs {max_source_length}"
        assert len(source_mask) == max_source_length
        assert len(similarity_ids) == max_source_length
        assert len(similarity_mask) == max_source_length
        
        # FIX: Test stage vẫn cần kiểm tra độ dài target
        assert len(target_ids) == max_target_length, \
            f"Target IDs length mismatch: {len(target_ids)} vs {max_target_length}"
        assert len(target_mask) == max_target_length
        
        features.append(InputFeatures(
            example_id=example.idx,
            source_ids=source_ids,
            source_mask=source_mask,
            similarity_ids=similarity_ids,
            similarity_mask=similarity_mask,
            target_ids=target_ids,
            target_mask=target_mask
        ))
        
        # Debug: In ra first example
        if example_idx == 0:
            print(f"\n*** Sample {stage} ***")
            print(f"idx: {example.idx}")
            print(f"source: {example.source[:50]}...")
            print(f"similarity: {example.similarity[:50]}...")
            print(f"target: {example.target[:50]}..." if stage != 'test' else "target: [TEST MODE]")
            print(f"source_ids length: {len(source_ids)}")
            print(f"target_ids length: {len(target_ids)}")
    
    return features


# ============================================================================
# EXPORTS
# ============================================================================
__all__ = [
    'set_seed',
    'Example',
    'InputFeatures', 
    'read_examples',
    'convert_examples_to_features'
]