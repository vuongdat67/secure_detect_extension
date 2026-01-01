"""
ROUGE-W Evaluation Module - Fixed version
Thay thế file utils/eval.py trong exploitgen-code dataset
"""
from typing import List
import numpy as np


def rouge_w_sentence_level(pred_tokens: List[str], ref_tokens: List[str]) -> tuple:
    """
    ROUGE-W (Weighted Longest Common Subsequence)
    
    WLCS ưu tiên các consecutive matches bằng cách tăng trọng số theo độ dài chuỗi khớp liên tiếp.
    
    Args:
        pred_tokens: List các token của prediction
        ref_tokens: List các token của reference
        
    Returns:
        tuple: (precision, recall, f1_score)
    """
    def wlcs(X: List[str], Y: List[str]) -> float:
        """
        Weighted Longest Common Subsequence
        
        Động lực: Thưởng cho các consecutive matches
        - Nếu X[i] == Y[j] và trước đó cũng match -> tăng weight
        - Weight function: (k+1)^2 - k^2 = 2k + 1
        """
        m, n = len(X), len(Y)
        
        # c[i][j]: WLCS score của X[0..i-1] và Y[0..j-1]
        c = [[0] * (n + 1) for _ in range(m + 1)]
        
        # w[i][j]: độ dài chuỗi consecutive matches kết thúc tại (i,j)
        w = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if X[i-1] == Y[j-1]:
                    # Token khớp
                    k = w[i-1][j-1]  # Độ dài consecutive trước đó
                    # Cộng thêm weight: (k+1)^2 - k^2
                    c[i][j] = c[i-1][j-1] + (k + 1) ** 2 - k ** 2
                    w[i][j] = k + 1  # Tăng độ dài consecutive
                else:
                    # Token không khớp -> chọn max từ trên hoặc trái
                    if c[i-1][j] > c[i][j-1]:
                        c[i][j] = c[i-1][j]
                    else:
                        c[i][j] = c[i][j-1]
                    w[i][j] = 0  # Reset consecutive counter
        
        return c[m][n]
    
    # Tính WLCS score
    wlcs_score = wlcs(pred_tokens, ref_tokens)
    
    ref_len = len(ref_tokens)
    pred_len = len(pred_tokens)
    
    # Edge case: empty sequences
    if ref_len == 0 or pred_len == 0:
        return 0.0, 0.0, 0.0
    
    # Normalize bằng bình phương độ dài (theo công thức ROUGE-W)
    recall = wlcs_score / (ref_len ** 2)
    precision = wlcs_score / (pred_len ** 2)
    
    # F1-score
    if recall + precision == 0:
        f1 = 0.0
    else:
        f1 = (2 * recall * precision) / (recall + precision)
    
    return precision, recall, f1


def evaluate_single(prediction: str, ground_truth: str) -> tuple:
    """
    Evaluate một cặp prediction-groundtruth
    
    Args:
        prediction: Chuỗi prediction
        ground_truth: Chuỗi ground truth
        
    Returns:
        tuple: (exact_match, rouge_w_f1)
    """
    gt_tokens = ground_truth.strip().split(" ")
    pred_tokens = prediction.strip().split(" ")
    
    # ROUGE-W F1 score
    _, _, rouge_w = rouge_w_sentence_level(pred_tokens, gt_tokens)
    
    # Exact match (0 hoặc 1)
    exact_match = float(prediction == ground_truth)
    
    return exact_match, rouge_w


def evaluate_list(prediction: List[str], ground_truth: List[str]) -> dict:
    """
    Evaluate toàn bộ dataset
    
    Args:
        prediction: List các predictions
        ground_truth: List các ground truths
        
    Returns:
        dict: {"acc": accuracy, "rouge-w": average ROUGE-W F1}
    """
    exact_match_scores = []
    rouge_scores = []
    
    for i in range(len(ground_truth)):
        em, rouge = evaluate_single(prediction[i], ground_truth[i])
        exact_match_scores.append(em)
        rouge_scores.append(rouge)
    
    return {
        "acc": np.mean(exact_match_scores),
        "rouge-w": np.mean(rouge_scores)
    }


def get_details(prediction: List[str], ground_truth: List[str]) -> tuple:
    """
    Lấy chi tiết từng sample (dùng cho Wilcoxon test)
    
    Args:
        prediction: List các predictions
        ground_truth: List các ground truths
        
    Returns:
        tuple: (rouge_scores_list, exact_match_scores_list)
    """
    exact_match_scores = []
    rouge_scores = []
    
    for i in range(len(ground_truth)):
        em, rouge = evaluate_single(prediction[i], ground_truth[i])
        exact_match_scores.append(em)
        rouge_scores.append(rouge)
    
    return rouge_scores, exact_match_scores