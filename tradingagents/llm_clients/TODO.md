# LLM 客户端一致性改进

## 待处理问题

### 1. `validate_model()` is never called
- 在 `get_llm()` 中补充校验调用；对未知模型给出警告，而不是直接报错

### 2. ~~参数处理不一致~~（已修复）
- `GoogleClient` 现在接受统一的 `api_key`，并映射为 `google_api_key`

### 3. ~~`base_url` 被接受但未生效~~（已修复）
- 所有客户端现在都会把 `base_url` 传递给各自的 LLM 构造函数

### 4. ~~将 CLI 中的模型同步到 `validators.py`~~（已修复）
- 已在 `v0.2.2` 中同步
