# Model Upload

After a verified LoRA run, stage adapter artifacts for Hugging Face:

```bash
hf auth login
hf repo create sebastianboehler/autoresearch-after-effects-lfm25-8b-a1b-lora --type model
hf upload sebastianboehler/autoresearch-after-effects-lfm25-8b-a1b-lora \
  artifacts/adapters/lfm25-8b-a1b-after-effects \
  --repo-type model
```

Model cards should include:

- base model
- dataset repo and revision
- verification summary
- AE version used for live checks
- render success rate when available
- known limitations
