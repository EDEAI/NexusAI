# GPG Text Plugin Development Progress

## Phase 1: Integration of Core Logic

- [x] Add `pgpy` dependency to `requirements.txt`.
- [x] Define separate tools for encrypt, decrypt, sign, verify, generate_key (YAML).
- [x] Implement Python tool classes calling `utils/the_gpg.py` functions.
- [x] Update `provider/gpg_text.yaml` to list new tools.
- [x] Update `manifest.yaml` description and tags.

## Phase 2: Refinement & Testing

- [x] Review all YAML files for consistency in descriptions and parameter naming.
- [ ] Implement basic credential validation in `provider/gpg_text.py` (if applicable, e.g., for a default key). Currently, keys are passed per tool.
- [ ] Add comprehensive unit tests for `utils/the_gpg.py`. (Skipped as per user request)
- [ ] Perform integration testing using Dify's local debugger or UI.
- [x] Update `README.md` with detailed usage instructions for each tool.
- [x] Create `PRIVACY.md` detailing data handling.
- [ ] Consider adding i18n for all user-facing strings (labels, descriptions). (Partially done)
- [x] [2025-04-19] Conducted plugin review and identified areas for improvement (i18n, cleanup, testing).

