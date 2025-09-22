"""
Utility functions for model operations
"""

def is_quantized_model(model):
    """
    Kiểm tra xem model có phải là quantized model không
    
    Args:
        model: The model to check
        
    Returns:
        bool: True if model is quantized, False otherwise
    """
    try:
        # Kiểm tra quantization_config
        if hasattr(model, 'config') and hasattr(model.config, 'quantization_config'):
            return True
            
        # Kiểm tra model name hoặc class name
        model_name = getattr(model, '__class__', '').__name__.lower()
        if 'quantized' in model_name or '4bit' in model_name or '8bit' in model_name:
            return True
            
        # Kiểm tra các attributes khác
        if hasattr(model, 'quantization_config'):
            return True
            
        return False
    except Exception:
        return False

def safe_to_device(tensor, model):
    """
    Đưa tensor lên device một cách an toàn, kiểm tra quantized model
    
    Args:
        tensor: Tensor to move to device
        model: Model to check for quantization
        
    Returns:
        Tensor on appropriate device
    """
    if is_quantized_model(model):
        # Model đã được quantized, không cần .to()
        return tensor
    else:
        # Model thường, cần đưa lên device
        return tensor.to(model.device)

def safe_tokenize_to_device(tokenizer, text, model, **kwargs):
    """
    Tokenize text và đưa lên device một cách an toàn
    
    Args:
        tokenizer: Tokenizer to use
        text: Text to tokenize
        model: Model to check for quantization
        **kwargs: Additional arguments for tokenizer
        
    Returns:
        Tokenized and device-mapped encoding
    """
    encoding = tokenizer(text, return_tensors="pt", **kwargs)
    
    if is_quantized_model(model):
        # Model đã được quantized, không cần .to()
        return encoding
    else:
        # Model thường, cần đưa lên device
        return {key: value.to(model.device) for key, value in encoding.items()}
