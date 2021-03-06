"""Retrieve and count the contents of a file"""

from pathlib import Path
import re

from gator import util

FILE_SEPARATOR = "/"

# References:
# https://stackoverflow.com/questions/18568105/how-match-a-paragraph-using-regex
# https://stackoverflow.com/questions/13531204/how-to-match-paragraphs-in-text-with-regx

CODE_FENCE_MARKER = "```"
GATORGRADER_REPLACEMENT = "GATORGRADER_REPLACEMENT"
PARAGRAH_RE = r"(.+?\n\n|.+?$)"
SECTION_MARKER = "#"

NEWLINE = "\n"
NOTHING = ""
SPACE = " "

DOUBLE_NEWLINE = NEWLINE * 2


def is_paragraph(candidate):
    """Determines if a writing candidate is a paragraph"""
    # remove whitespace surrounding candidate paragraph
    candidate = candidate.strip()
    # if the paragraph is a markdown header, it is not a paragraph
    if candidate.startswith(SECTION_MARKER):
        return False
    # if the paragraph is a fenced code block, it is not a paragraph
    if candidate.startswith(CODE_FENCE_MARKER):
        return False
    # there may be other edge cases that should be added here in the
    # future -- what other structures look like paragraphs but should
    # not be?
    # if nothing has returned by now, the candidate must be a paragraph
    return True


def get_paragraphs(contents, blank_replace=True):
    """Retrieves the paragraphs in the writing"""
    # use a replacement to handle a string with just spaces
    if blank_replace is True:
        contents = contents.replace(SPACE, NOTHING)
    # replace a single newline with a blank space, respecting double newlines
    contents = contents.replace(DOUBLE_NEWLINE, GATORGRADER_REPLACEMENT)
    contents = contents.replace(NEWLINE, SPACE)
    contents = contents.replace(GATORGRADER_REPLACEMENT, DOUBLE_NEWLINE)
    pattern = re.compile(PARAGRAH_RE)
    paragraphs = pattern.findall(contents)
    # disregard all of the section headers in markdown
    matching_paragraphs = []
    # iterate through all potential paragraphs and gather
    # those that match the standard for legitimacy
    for paragraph in paragraphs:
        if is_paragraph(paragraph) is True:
            matching_paragraphs.append(paragraph)
    return matching_paragraphs


def get_line_list(content):
    """Returns a list of lines from any type of input string"""
    actual_content = []
    # iteratively decode each of the lines in the content
    for line in content.splitlines(keepends=False):
        # decode worked for this content and charset, use decoded
        try:
            current_line_decoded = line.decode()
        # decode worked for this content and charset, use line
        except AttributeError:
            current_line_decoded = line
        # the decoded line is not a blank space (e.g., "")
        # so it should be added into the list of lines
        # the goal is to avoid counting blank lines
        if not is_blank_line(current_line_decoded):
            actual_content.append(current_line_decoded)
    return actual_content


def is_blank_line(line):
    """Returns True if a line is a blank one and False otherwise"""
    if line is not None and line is not NOTHING and not line.isspace():
        return False
    return True


def count_paragraphs(contents):
    """Counts the number of paragraphs in the writing"""
    replace_blank_inputs = True
    matching_paragraphs = get_paragraphs(contents, replace_blank_inputs)
    return len(matching_paragraphs)


def count_words(contents):
    """Counts the minimum number of words across all paragraphs in writing"""
    # retrieve all of the paragraphs in the contents
    replace_blank_inputs = False
    paragraphs = get_paragraphs(contents, replace_blank_inputs)
    # count all of the words in each paragraph
    word_counts = []
    for para in paragraphs:
        para = para.replace(NEWLINE, SPACE)
        words = NOTHING.join(ch if ch.isalnum() else SPACE for ch in para).split()
        word_counts.append(len(words))
    # return the minimum number of words across all paragraphs
    if word_counts:
        return min(word_counts)
    # counting did not work correctly, so return 0
    return 0


def count_specified_fragment(contents, fragment):
    """Counts the specified string fragment in the string contents"""
    fragment_count = contents.count(fragment)
    return fragment_count


# pylint: disable=bad-continuation
def specified_fragment_greater_than_count(
    chosen_fragment,
    checking_function,
    expected_count,
    given_file=NOTHING,
    containing_directory=NOTHING,
    contents=NOTHING,
    exact=False,
):
    """Determines if the fragment count is greater than expected"""
    # count the fragments in either a file in a directory or String contents
    file_fragment_count = count_fragments(
        chosen_fragment, checking_function, given_file, containing_directory, contents
    )
    # check the condition and also return file_fragment_count
    return util.greater_than_equal_exacted(file_fragment_count, expected_count, exact)


# pylint: disable=bad-continuation
def count_fragments(
    chosen_fragment,
    checking_function,
    given_file=NOTHING,
    containing_directory=NOTHING,
    contents=NOTHING,
):
    """Counts fragments for the file in the directory (or contents) and a fragment"""
    file_for_checking = Path(containing_directory + FILE_SEPARATOR + given_file)
    file_contents_count = 0
    # file is not available and the contents are provided
    if not file_for_checking.is_file() and contents is not NOTHING:
        file_contents_count = checking_function(contents, chosen_fragment)
    # file is available and the contents are not provided
    elif file_for_checking.is_file() and contents is NOTHING:
        file_contents = file_for_checking.read_text()
        file_contents_count = checking_function(file_contents, chosen_fragment)
    return file_contents_count


# pylint: disable=bad-continuation
def specified_source_greater_than_count(
    expected_count,
    given_file=NOTHING,
    containing_directory=NOTHING,
    contents=NOTHING,
    exact=False,
):
    """Determines if the line count is greater than expected"""
    # count the fragments in either a file in a directory or String contents
    file_line_count = count_lines(given_file, containing_directory, contents)
    # the fragment count is at or above the threshold
    # check the condition and also return file_fragment_count
    return util.greater_than_equal_exacted(file_line_count, expected_count, exact)


def count_lines(given_file=NOTHING, containing_directory=NOTHING, contents=NOTHING):
    """Counts lines for the file in the directory (or contents)"""
    file_for_checking = Path(containing_directory + FILE_SEPARATOR + given_file)
    file_contents_count = 0
    # file is not available and the contents are provided
    if not file_for_checking.is_file() and contents is not NOTHING:
        line_list = get_line_list(contents)
        file_contents_count = len(line_list)
    # file is available and the contents are not provided
    elif file_for_checking.is_file() and contents is NOTHING:
        file_contents = file_for_checking.read_text()
        line_list = get_line_list(file_contents)
        file_contents_count = len(line_list)
    return file_contents_count
