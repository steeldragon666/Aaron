name: stegg

description: Full ST3GG steganography toolkit access — encode, decode, analyze, and detect hidden data across images, audio, text, and documents. Access all 112+ techniques including LSB, DCT, F5, SPECTER cipher, and steganalysis.

user-invocable: true

# /stegg — Full ST3GG Toolkit

Access the complete ST3GG steganography platform. For quick-access presets use:
- `/secretsquirrel` — ghost mode (AES-256 encrypted, maximum stealth)
- `/reallysecretsquirrel` — matryoshka mode (recursive multi-layer nesting)

## Setup (first use)

```bash
pip install stegg
```

## Commands

```
/stegg encode <image> "<message>" [options]
/stegg decode <image> [options]
/stegg analyze <image>
/stegg capacity <image>
/stegg specter <image> "<message>" -o <output>
/stegg text hide "<message>" "<cover_text>"
/stegg help
```

## ENCODE — Hide data in an image

```bash
stegg encode -i <carrier_image> --text "<message>" -o <output_image> [options]
stegg encode -i <carrier_image> --file <file_to_hide> -o <output_image> [options]
```

### Key options:
| Flag | Description | Default |
|------|-------------|---------|
| `--bits 1-8` | Bits per channel (1=minimal footprint, 8=max capacity) | 1 |
| `--strategy interleaved` | Encoding pattern — ALWAYS use this | interleaved |
| `--channels RGB` | Channel preset (R, G, B, A, RGB, RGBA, RG, etc.) | RGB |
| `--password <key>` | AES-256 encrypt payload + derive hidden header magic | none |
| `--no-compress` | Skip payload compression | off |

### CRITICAL: Always use `--strategy interleaved` — spread and randomized have decode bugs.

### Examples:
```bash
# Basic encode
stegg encode -i photo.png --text "hello" -o out.png

# Encrypted encode (recommended)
stegg encode -i photo.png --text "secret" --password mykey -o out.png --bits 2

# Hide a file
stegg encode -i photo.png --file secret.pdf --password mykey -o out.png --bits 3

# Maximum capacity (high visibility risk)
stegg encode -i photo.png --text "long message" --bits 4 --channels RGBA -o out.png
```

## DECODE — Extract hidden data

```bash
stegg decode -i <stego_image> [--password <key>] [-o <output_file>]
```

Auto-detect is on by default with interleaved strategy. For binary output:
```bash
stegg decode -i out.png --password mykey -o recovered.pdf
```

## ANALYZE — Detect hidden data in an image

```bash
stegg analyze <image> --full
```

Returns chi-square analysis, LSB anomaly scores, capacity estimates, and suspicion rating. Use this to test whether your stego image passes detection.

## CAPACITY — How much can I hide?

```bash
stegg analyze <image>
```

The analysis output includes available capacity at 1-bit and 2-bit depth.

## SPECTER — Channel cipher mode

Distributes data across color channels using a pattern key. Triggered by special payload syntax:

```bash
stegg encode -i photo.png --text "{SPECTER:ENABLED}" --password mykey -o out.png
```

## TEXT STEGANOGRAPHY — Hide in plain text

ST3GG supports Unicode zero-width character injection for hiding data inside normal-looking text. Use the browser interface at https://ste.gg for text steganography (no CLI equivalent currently).

## AUDIO STEGANOGRAPHY

```bash
stegg encode -i audio.wav --text "message" -o stego.wav
stegg decode -i stego.wav
```

## STEGANALYSIS — Find hidden data in unknown files

```bash
stegg analyze suspicious.png --full
stegg analyze suspicious.wav
```

## Workflow rules
1. ALWAYS verify encode → decode roundtrip before distributing stego files
2. ALWAYS use `--strategy interleaved`
3. Check JSON for `"error"` keys before chaining operations
4. `--bits 1` for stealth, `--bits 2-3` for capacity+stealth balance, `--bits 4+` only when capacity is critical and visual detection is acceptable
5. Passwords must match exactly between encode and decode

## Quick reference
| Goal | Command |
|------|---------|
| Hide text, basic | `stegg encode -i img.png --text "msg" -o out.png` |
| Hide text, encrypted | `stegg encode -i img.png --text "msg" -p key -o out.png --bits 2` |
| Hide a file | `stegg encode -i img.png --file secret.zip -p key -o out.png --bits 3` |
| Retrieve | `stegg decode -i out.png -p key` |
| Detect | `stegg analyze img.png --full` |
| Ghost mode | Use `/secretsquirrel` |
| Matryoshka | Use `/reallysecretsquirrel` |
