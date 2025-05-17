#!/usr/bin/env python3

import os
import sys
import json
import tempfile
import argparse
import logging
from pathlib import Path
from dotenv import load_dotenv
from pydub import AudioSegment
from pydub.utils import make_chunks
from deepgram import DeepgramClient, PrerecordedOptions
from tqdm import tqdm

# === ASCII Art Banner ===
BANNER = r'''

    ██████  ██████  ██████  ██████        ███████ ██████  ██████  ██   ██ ██   ██ 
    ██   ██      ██      ██ ██   ██       ██      ██   ██      ██ ██   ██ ██  ██  
    ██   ██  █████   █████  ██████  █████ ███████ ██████   █████  ███████ █████   
    ██   ██      ██      ██ ██                 ██ ██           ██      ██ ██  ██  
    ██████  ██████  ██████  ██            ███████ ██      ██████       ██ ██   ██ 
                                                                                             
                                                                       
'''

# Constants
MAX_SIZE = 2 * 1024 ** 3  # 2 GB
AUDIO_EXTS = {'.mp3', '.wav', '.flac', '.m4a', '.ogg'}
VIDEO_EXTS = {'.mp4', '.mov', '.avi', '.mkv'}


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def extract_audio(input_path: Path) -> Path:
    output_audio = input_path.with_suffix('.wav')
    logging.info(f"Extracting audio from video {input_path} -> {output_audio}")
    audio = AudioSegment.from_file(str(input_path))
    audio.export(str(output_audio), format='wav')
    return output_audio


def transcribe_whole(deepgram: DeepgramClient, filepath: Path, options: PrerecordedOptions):
    logging.info(f"Transcribing entire file {filepath} ({filepath.stat().st_size} bytes)")
    with filepath.open('rb') as f:
        source = {'buffer': f, 'mimetype': f'audio/{filepath.suffix.lstrip('.')}' }
        response = deepgram.listen.rest.v('1').transcribe_file(source, options)
    return json.loads(response.to_json())


def transcribe_chunks(deepgram: DeepgramClient, filepath: Path, options: PrerecordedOptions, chunk_minutes: int):
    logging.info(f"Chunking audio into {chunk_minutes}-minute segments")
    audio = AudioSegment.from_file(str(filepath))
    chunks = make_chunks(audio, chunk_minutes * 60 * 1000)
    results = []
    for i, chunk in enumerate(tqdm(chunks, desc='Chunks')):
        logging.info(f"Processing chunk {i+1}/{len(chunks)}")
        tmp = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        chunk.export(tmp.name, format='wav')
        tmp.close()
        with open(tmp.name, 'rb') as f:
            source = {'buffer': f, 'mimetype': 'audio/wav'}
            resp = deepgram.listen.rest.v('1').transcribe_file(source, options)
        os.unlink(tmp.name)
        results.append(json.loads(resp.to_json()))
    return results


def transcribe_file(args):
    # Load environment
    load_dotenv()
    api_key = os.getenv('DEEPGRAM_API_KEY')
    if not api_key:
        logging.error('DEEPGRAM_API_KEY not set')
        sys.exit(1)

    # Logging
    setup_logging()

    input_path = Path(args.file)
    if not input_path.exists():
        logging.error(f"File not found: {input_path}")
        sys.exit(1)

    # Handle video
    if input_path.suffix.lower() in VIDEO_EXTS:
        input_path = extract_audio(input_path)

    size = input_path.stat().st_size
    deepgram = DeepgramClient(api_key)

    # Configure options
    options = PrerecordedOptions(
        model=args.model,
        language=args.language,
        smart_format=True,
        punctuate=True,
        paragraphs=True,
        utterances=args.utterances
    )
    logging.info(f"Options: model={args.model}, language={args.language}, utterances={args.utterances}")

    # Transcription
    json_outputs = []
    if size <= MAX_SIZE:
        json_outputs = [transcribe_whole(deepgram, input_path, options)]
    else:
        logging.info(f"File size {size} > 2GB, chunking")
        json_outputs = transcribe_chunks(deepgram, input_path, options, args.chunk_length)

    # Aggregate text
    transcripts = []
    for data in json_outputs:
        text = data['results']['channels'][0]['alternatives'][0]['transcript']
        transcripts.append(text.replace('\\n', '\n'))

    output = '\n'.join(transcripts)
    if args.output:
        Path(args.output).write_text(output, encoding='utf-8')
        logging.info(f"Saved transcript to {args.output}")
    else:
        print(output)


def main():
    parser = argparse.ArgumentParser(
        description='D33P-5P34K: a transcription tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='See README or --help for details.'
    )
    parser.add_argument('--file', '-f', required=True,
                        help='Path to audio/video file')
    parser.add_argument('--model', default='nova-2',
                        help='Deepgram model (nova-2, nova-3, whisper)')
    parser.add_argument('--language', default='it',
                        help='Language code (e.g., en, it, es)')
    parser.add_argument('--utterances', action='store_true',
                        help='Include utterance timestamps and speaker info')
    parser.add_argument('--chunk-length', type=int, default=10,
                        help='Minutes per chunk if file > 2GB')
    parser.add_argument('--output', '-o',
                        help='Output transcript file (defaults to stdout)')
    args = parser.parse_args()
    transcribe_file(args)

if __name__ == '__main__':
    print(BANNER)
    main()
