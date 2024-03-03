#!/usr/bin/env python3

import re
import argparse
from typing import List, Tuple

def bold_keywords(text: str, keywords: List[str]) -> str:
    """Bold the keywords in the text using Markdown syntax."""
    bolded_text = text
    for word in keywords:
        bolded_text = re.sub(fr'\b({word})\b', r'**\1**', bolded_text, flags=re.IGNORECASE)
    return bolded_text

def find_word_blobs(text: str, keywords: List[str], before: int = 10, after: int = 10) -> List[str]:
    """Find and return blobs of words containing the keywords."""
    words = text.split()
    keyword_indices = []
    for i, word in enumerate(words):
        if any(re.search(fr'\b{keyword}\b', word, re.IGNORECASE) for keyword in keywords):
            keyword_indices.append(i)

    blobs = []
    for index in keyword_indices:
        start = max(index - before, 0)
        end = min(index + after + 1, len(words))
        blob = ' '.join(words[start:end])
        blobs.append((start, end, blob))

    return merge_overlapping_blobs(blobs, keywords)

def merge_overlapping_blobs(blobs: List[Tuple[int, int, str]], keywords: List[str]) -> List[str]:
    """Merge overlapping blobs based on their indices."""
    merged_blobs = []
    current_blob = None

    for start, end, text in blobs:
        if current_blob and start <= current_blob[1]:
            # Extend the current blob
            new_end = max(end, current_blob[1])
            new_text = ' '.join(set(current_blob[2].split() + text.split()))
            current_blob = (current_blob[0], new_end, new_text)
        else:
            if current_blob:
                merged_blobs.append(bold_keywords(current_blob[2], keywords))
            current_blob = (start, end, text)

    if current_blob:
        merged_blobs.append(bold_keywords(current_blob[2], keywords))

    return merged_blobs


def parse_arguments():
    """Parse command line arguments."""
    before_default = 10
    after_default = 10
    parser = argparse.ArgumentParser(description='Search for words in a text file and display surrounding words.')
    parser.add_argument('file_path', help='Path to the text file')
    parser.add_argument('keywords', nargs='+', help='List of keywords to search for')
    parser.add_argument('-b', '--before', type=int, default=before_default, help=f'Number of words before the keyword. Default is {before_default}.')
    parser.add_argument('-a', '--after',  type=int, default=after_default , help=f'Number of words after the keyword. Default is {after_default}.')
    parser.add_argument('-o', '--output', help='Output file path (optional)')
    return parser.parse_args()

def main():
    args = parse_arguments()

    with open(args.file_path, 'r') as file:
        text = file.read()

    blobs = find_word_blobs(text, args.keywords, args.before, args.after)

    output_text = "\n\n".join(blobs)

    if args.output:
        with open(args.output, 'w') as output_file:
            output_file.write(output_text)
    else:
        print(output_text)

if __name__ == "__main__":
    main()
