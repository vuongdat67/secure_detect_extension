import os
from model import CodeBert_Seq2Seq
from utils import set_seed

# ===== KAGGLE PATHS =====
KAGGLE_INPUT = '/kaggle/input'
KAGGLE_WORKING = '/kaggle/working'

# Input datasets
DATA_DIR = f'{KAGGLE_INPUT}/exploitgen-data'
SPOC_PATH = f'{DATA_DIR}/spoc/spoc-train.tsv'

# Checkpoints (sẽ load từ DAPT/TAPT đã train)
DAPT_MODEL = f'{KAGGLE_INPUT}/exploitgen-dapt-model'  # Dataset chứa DAPT checkpoint
TAPT_MODEL = f'{KAGGLE_INPUT}/exploitgen-tapt-model'  # Dataset chứa TAPT checkpoint

# Output directories
OUTPUT_STAGE1_RAW = f'{KAGGLE_WORKING}/stage1-raw-encoder'
OUTPUT_STAGE1_TEMP = f'{KAGGLE_WORKING}/stage1-temp-encoder'
OUTPUT_FINAL = f'{KAGGLE_WORKING}/exploitgen-final'

os.makedirs(OUTPUT_STAGE1_RAW, exist_ok=True)
os.makedirs(OUTPUT_STAGE1_TEMP, exist_ok=True)
os.makedirs(OUTPUT_FINAL, exist_ok=True)

# ===== CONFIG =====
set_seed(42)

# Chọn ngôn ngữ để train
LANGUAGE = 'assembly'  # hoặc 'python'

# Paths theo ngôn ngữ
if LANGUAGE == 'assembly':
    TRAIN_DATA = f'{DATA_DIR}/assembly/train.csv'
    DEV_DATA = f'{DATA_DIR}/assembly/dev.csv'
    TEST_DATA = f'{DATA_DIR}/assembly/test.csv'
else:
    TRAIN_DATA = f'{DATA_DIR}/python/train.csv'
    DEV_DATA = f'{DATA_DIR}/python/dev.csv'
    TEST_DATA = f'{DATA_DIR}/python/test.csv'

print("="*80)
print(f"TRAINING EXPLOITGEN - {LANGUAGE.upper()}")
print("="*80)
print(f"Train data: {TRAIN_DATA}")
print(f"Dev data:   {DEV_DATA}")
print(f"Test data:  {TEST_DATA}")
print(f"TAPT model: {TAPT_MODEL}")
print("="*80)

# ===== STAGE 1A: Train Raw Encoder =====
print("\n[STAGE 1A] Training Raw Encoder...")

model_raw = CodeBert_Seq2Seq(
    ip_path=TAPT_MODEL,      # Load từ FG-CodeBERT (TAPT)
    raw_path=TAPT_MODEL,     # Cùng base model
    decoder_layers=6,
    fix_encoder=False,       # Cho phép fine-tune encoder
    beam_size=10,
    max_source_length=64,
    max_target_length=64,
    load_model_path=None,    # Train from scratch
    layer_attention=False,   # Stage 1 không dùng attention
    l2_norm=False,
    fusion=False
)

model_raw.train(
    train_filename=TRAIN_DATA,
    train_batch_size=32,
    num_train_epochs=5,      # Tác giả dùng ~5 epochs
    learning_rate=4e-5,
    do_eval=True,
    dev_filename=DEV_DATA,
    eval_batch_size=64,
    output_dir=OUTPUT_STAGE1_RAW,
    gradient_accumulation_steps=1
)

print(f"✓ Raw Encoder saved to {OUTPUT_STAGE1_RAW}")

# ===== STAGE 1B: Train Template Encoder =====
print("\n[STAGE 1B] Training Template Encoder...")

model_temp = CodeBert_Seq2Seq(
    ip_path=TAPT_MODEL,
    raw_path=TAPT_MODEL,
    decoder_layers=6,
    fix_encoder=False,
    beam_size=10,
    max_source_length=64,
    max_target_length=64,
    load_model_path=None,
    layer_attention=False,
    l2_norm=False,
    fusion=False
)

# Dataset cho template encoder: input là temp_nl, output là temp_code
model_temp.train(
    train_filename=TRAIN_DATA,
    train_batch_size=32,
    num_train_epochs=5,
    learning_rate=4e-5,
    do_eval=True,
    dev_filename=DEV_DATA,
    eval_batch_size=64,
    output_dir=OUTPUT_STAGE1_TEMP,
    gradient_accumulation_steps=1
)

print(f"✓ Template Encoder saved to {OUTPUT_STAGE1_TEMP}")

# ===== STAGE 2: Train Full ExploitGen =====
print("\n[STAGE 2] Training Full ExploitGen Model...")

model_final = CodeBert_Seq2Seq(
    ip_path=f'{OUTPUT_STAGE1_TEMP}/encoder',   # Load template encoder
    raw_path=f'{OUTPUT_STAGE1_RAW}/encoder',   # Load raw encoder
    decoder_layers=6,
    fix_encoder=False,
    beam_size=10,
    max_source_length=64,
    max_target_length=64,
    load_model_path=None,  # Không load full model, chỉ load 2 encoder riêng
    layer_attention=True,  # BẬT semantic attention
    l2_norm=True,          # BẬT L2 norm
    fusion=True            # BẬT fusion layer
)

model_final.train(
    train_filename=TRAIN_DATA,
    train_batch_size=8,           # Nhỏ hơn vì model lớn
    num_train_epochs=50,          # Tác giả dùng 50 epochs với early stopping
    learning_rate=4e-5,
    do_eval=True,
    dev_filename=DEV_DATA,
    eval_batch_size=16,
    output_dir=OUTPUT_FINAL,
    gradient_accumulation_steps=4  # Simulate batch_size=32
)

print(f"✓ Final model saved to {OUTPUT_FINAL}")

# ===== EVALUATION =====
print("\n[EVALUATION] Testing on test set...")

# Load best model
best_model_path = f'{OUTPUT_FINAL}/checkpoint-best-rouge/pytorch_model.bin'

model_eval = CodeBert_Seq2Seq(
    ip_path=f'{OUTPUT_STAGE1_TEMP}/encoder',
    raw_path=f'{OUTPUT_STAGE1_RAW}/encoder',
    decoder_layers=6,
    fix_encoder=False,
    beam_size=10,
    max_source_length=64,
    max_target_length=64,
    load_model_path=best_model_path,
    layer_attention=True,
    l2_norm=True,
    fusion=True
)

model_eval.test(
    test_filename=TEST_DATA,
    test_batch_size=16,
    output_dir=f'{OUTPUT_FINAL}/test_results'
)

print("\n" + "="*80)
print("TRAINING COMPLETE!")
print("="*80)
print(f"Results saved to: {OUTPUT_FINAL}/test_results")
print("Download test_hyp.csv and test_ref.csv to compare with paper")