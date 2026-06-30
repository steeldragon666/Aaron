name: reallysecretsquirrel

description: Matryoshka-mode steganography — recursive multi-layer image-in-image encoding. Hides a message in an image, then hides THAT image inside another image, repeating N times. Each layer has its own password. Reverse-unwraps automatically on decode.

user-invocable: true

# /reallysecretsquirrel — Matryoshka Mode Steganography

True nested steganography: the message is encoded into a carrier, then that carrier is itself hidden inside another image, recursively — like Russian nesting dolls. Each layer uses its own password and bit depth. To decode, you must unwrap every layer in reverse order.

Default depth: 3 layers. Max practical depth: 8 (beyond that, image quality degrades noticeably).

## Setup (first use)

```bash
pip install stegg
```

## Usage

```
/reallysecretsquirrel encode <carrier_image> "<message>" -o <output_image> --layers <N> --passwords <p1,p2,p3>
/reallysecretsquirrel decode <stego_image> --passwords <p3,p2,p1>
```

### Examples
```
/reallysecretsquirrel encode photo.png "the treasure is buried" -o nested.png --layers 3 --passwords alpha,beta,gamma
/reallysecretsquirrel decode nested.png --passwords gamma,beta,alpha
```

If no passwords provided, Claude will auto-generate them and show them to the user.

## How to execute — ENCODE

Matryoshka requires multiple sequential `stegg encode` calls. Each intermediate output becomes the next layer's payload (encoded as a file, not text).

### Layer-by-layer process:

**Layer 1 — encode the actual message:**
```bash
stegg encode -i <carrier> --text "<message>" --bits 2 --strategy interleaved --password <p1> -o /tmp/layer1.png
```

**Layer 2 — encode layer1 output as a FILE into another carrier:**
```bash
stegg encode -i <carrier> --file /tmp/layer1.png --bits 2 --strategy interleaved --password <p2> -o /tmp/layer2.png
```

**Layer 3 — encode layer2 output as a FILE into the final carrier:**
```bash
stegg encode -i <carrier> --file /tmp/layer2.png --bits 2 --strategy interleaved --password <p3> -o <final_output>
```

Note: The same carrier image can be reused at each layer, or different carriers can be used for added confusion. Different carriers is recommended for maximum stealth.

## How to execute — DECODE

Reverse the layer order and passwords:

**Unwrap layer 3 (outermost):**
```bash
stegg decode -i <stego_image> --password <p3> -o /tmp/unwrap2.png
```

**Unwrap layer 2:**
```bash
stegg decode -i /tmp/unwrap2.png --password <p2> -o /tmp/unwrap1.png
```

**Unwrap layer 1 (innermost — reveals the message):**
```bash
stegg decode -i /tmp/unwrap1.png --password <p1>
```

## Rules
1. ALWAYS use `--strategy interleaved` on every layer — never deviate
2. ALWAYS verify the full decode roundtrip after encoding before reporting success
3. Passwords must be given in REVERSE ORDER on decode (outermost layer first)
4. Use `/tmp/` for intermediate layer files — clean them up after
5. Different carrier images per layer provide the highest stealth (attacker must find AND decode all carriers)
6. Check for `"error"` keys in JSON output at each step; abort and report if any layer fails
7. Keep `--bits` at 2 for all layers — higher bits compound visual artifacts across layers

## Auto-password generation
If the user doesn't specify passwords, generate N random 12-character alphanumeric passwords and display them clearly:
```
Layer 1 password (innermost): xK9mPqR3vL2n
Layer 2 password:              Tz7wBnY4jF8c
Layer 3 password (outermost): Qp5hCxM6sA1e
SAVE THESE. Decode requires them in reverse order: Qp5hCxM6sA1e → Tz7wBnY4jF8c → xK9mPqR3vL2n
```

## What makes this "really secret"
- An attacker must: (1) detect there's steganography at all, (2) find the right password for each layer, (3) know how many layers exist, (4) decode every layer in the correct order
- Each layer independently passes visual steganalysis — the inner layers look like normal PNG data to the outer layer's decoder
- With different carrier images, the attacker doesn't even know the files are related

## Output format
Report back:
- ✓ Matryoshka encoding complete: <N> layers
- Final output: `<output_file>`
- Layer passwords (SAVE THESE):
  - Layer 1 (innermost): <p1>
  - Layer 2: <p2>
  - Layer N (outermost): <pN>
- Decode order: outermost → innermost (passwords in reverse)
- Full roundtrip verified: ✓
