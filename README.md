**Masking Binary Payloads within High-Entropy Video Containers.**

Most discussions around "Infinite Storage Glitches" focus on the novelty of free cloud space. This project, **Static Carrier**, approaches the concept from a Cybersecurity perspective, specifically focusing on **Information Hiding** and **Signature Erasure.** The goal was to build a utility that evaluates how multimedia containers can be used to encapsulate sensitive data. By serializing binary data into high-entropy visual "static," we can effectively mask a file's "Magic Bytes" and payload patterns, making them invisible to traditional inspection tools.

## The Security Research Angle

Traditional security stacks (DLP, IDS, AV) are optimized to flag known file types. If you try to move a `.zip` or an `.exe` through a monitored gateway, it is often flagged based on its signature.

**Static Carrier** demonstrates how to bypass these perimeters by:

- **Signature Erasure:** Converting an executable or archive into a stream of pixels. To a scanner, the file identity is strictly "MPEG-4 Video."
- **Entropy Obfuscation:** Using NumPy to generate high-frequency noise that mimics camera sensor artifacts or "TV snow," defeating simple pattern-matching engines.
- **Carrier Trust:** Exploiting the fact that multimedia traffic is often treated as "low-risk" or trusted noise in corporate environments.

## How it Works

- **Smart Header:** I utilized Python's `struct` module to pack an 8-byte size and a 64-byte extension string into the first frame. This allows the decoder to reconstruct the file perfectly without needing external metadata.
- **Bit-to-Pixel Mapping:** Data is unpacked into bits and mapped to 0 (black) or 255 (white) pixels.
- **H.264 Resilience:** The tool utilizes OpenCV to ensure the bitstream survives the initial quantization of the H.264 codec, maintaining data integrity during the encapsulation process.

## Getting Started

### 1. Installation

Clone the repository and install the dependencies:

`git clone https://github.com/YOUR_USERNAME/Static-Carrier-PoC.git
cd Static-Carrier-PoC
pip install -r requirements.txt`

### 2. Basic Usage

**To encapsulate a file (Encode):**

`python StaticCarrierPoC.py -e -i sensitive_payload.zip -o vault.mp4`

**To retrieve a file (Decode):**

`python StaticCarrierPoC.py -d -i vault.mp4`

**To hide a simple text message:**

`python StaticCarrierPoC.py -e -t -i "Secret credential string" -o message.mp4`