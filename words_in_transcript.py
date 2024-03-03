#!/usr/bin/env python3

import re
import argparse
from typing import List, Tuple

def bold_keywords(text: str, keywords: List[str]) -> str:
    """Bold the keywords in the text using Markdown syntax."""
    for word in keywords:
        # Using a regex pattern to match the word as a whole word, case-insensitive
        pattern = re.compile(fr'\b{re.escape(word)}\b', re.IGNORECASE)
        text = pattern.sub(r'**\g<0>**', text)
    return text

def find_keyword_indices(text: str, keywords: List[str]) -> Tuple[List[int],int]:
    """Find the indices of all occurrences of the keywords."""
    words = text.split()
    keyword_indices = []
    for i, word in enumerate(words):
        if any(re.search(fr'\b{keyword}\b', word, re.IGNORECASE) for keyword in keywords):
            keyword_indices.append(i)
    return keyword_indices, len(words)


def identify_blob_boundaries(keyword_indices: List[int], before: int, after: int) -> List[Tuple[int, int]]:
    """Identify start and end boundary keyword pairs that are not within the specified before or after distance of any other keyword."""
    boundaries = []
    i = 0
    while i < len(keyword_indices):
        start = keyword_indices[i]
        end = start

        #while i + 1 < len(keyword_indices) and keyword_indices[i + 1] - end <= after:
        while  i + 1 < len(keyword_indices) and keyword_indices[i + 1] - end <= before + after:
            i += 1
            end = keyword_indices[i]

        boundaries.append((start, end))
        i += 1

    return boundaries

def form_blobs(text: str, boundaries: List[Tuple[int, int]], before: int, after: int) -> List[str]:
    """Form blobs from keyword pairs, where the start of the blob is the start keyword's index minus the before distance and the end of the blob is the end keyword's index plus the after distance."""
    words = text.split()
    blobs = []
    for start, end in boundaries:
        blob_start = max(start - before, 0)
        blob_end   = min(end + after + 1, len(words))
        blob_text  = ' '.join(words[blob_start:blob_end])
        blobs.append(f"({blob_start},{blob_end}): {blob_text}")

    return blobs

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

    keyword_indices, total_words = find_keyword_indices(text, args.keywords)
    boundaries = identify_blob_boundaries(keyword_indices, args.before, args.after)
    blobs = form_blobs(text, boundaries, args.before, args.after)

    output_text = f"Document: {args.file_path}\n"
    output_text += f"Total number of words: {total_words}. Words (before,after) keywords = ({args.before},{args.after}).\n\n"

    # Apply bold_keywords to each blob and join into one big string for output
    output_text += "\n\n".join(bold_keywords(blob, args.keywords) for blob in blobs)

    if args.output:
        with open(args.output, 'w') as output_file:
            output_file.write(output_text)
    else:
        print(output_text)
        

if __name__ == "__main__":
    main()
