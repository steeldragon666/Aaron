name: secretsquirrel

description: Ghost-mode steganography — hide encrypted secret messages inside images using AES-256 password protection, high bit depth, and interleaved encoding. Maximum stealth, minimum detectability.

user-invocable: true

# /secretsquirrel — Ghost Mode Steganography

Hides a secret message inside an image with maximum stealth:
- AES-256-GCM encryption via HMAC-derived password magic (header becomes undetectable without the key)
- 2-bit depth per channel (visually imperceptible, ~4x capacity of 1-bit)
- Interleaved strategy (the only strategy with reliable auto-detect on decode)
- Always verifies the encode/decode roundtrip before reporting success

## Setup (first use)

Ensure ST3GG is installed:
```bash
pip install stegg
```

## Usage

```
/secretsquirrel encode <carrier_image> "<message>" -o <output_image> -p <password>
/secretsquirrel decode <stego_image> -p <password>
/secretsquirrel capacity <image>
```

### Examples
```
/secretsquirrel encode photo.png "meet at dawn" -o out.png -p mykey123
/secretsquirrel decode out.png -p mykey123
/secretsquirrel capacity photo.png
```

## How to execute each command

### ENCODE
Run this bash command:
```bash
stegg encode -i <carrier_image> -o <output_image> --text "<message>" --bits 2 --strategy interleaved --password <password>
```
Then immediately verify with decode (see below). Only report success after the roundtrip confirms the message.

### DECODE
```bash
stegg decode -i <stego_image> --password <password>
```

### CAPACITY CHECK
```bash
stegg encode -i <image> --text "test" --bits 2 --strategy interleaved --password test -o /tmp/cap_test.png
stegg analyze <image> --full
```

## Rules
1. ALWAYS verify encode → decode roundtrip before reporting success
2. ALWAYS use `--strategy interleaved` — other strategies have upstream decode bugs
3. ALWAYS use `--bits 2` for ghost-mode stealth balance (or `--bits 1` for absolute minimum footprint)
4. If the user doesn't provide a password, prompt them for one — the password IS the encryption key
5. Check JSON output for `"error"` keys before proceeding
6. Never use `--bits` above 3 — higher values become visually detectable

## What makes this "ghost mode"
- The `--password` flag triggers HMAC-SHA256 derived magic bytes — the steg header is unrecognizable without the exact password
- Anyone running standard steg detection without the password sees noise
- At 2 bits per channel, pixel changes are ±1-3 RGB values — below human perception threshold

## Output format
Report back:
- ✓ Encoded successfully into `<output_file>`
- Capacity used: X bytes of Y available
- Decode verified: ✓
- Password required to retrieve: [remind user to keep it safe]
