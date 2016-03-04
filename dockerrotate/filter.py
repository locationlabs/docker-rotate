import re


def include_image(image_tags, args):
    """
    Return truthy if image should be considered for removal.
    """
    if not args.images:
        return True

    return all(regex_match(pattern, tag)
               for pattern in args.images
               for tag in image_tags)


def regex_match(pattern, tag):
    """
    Perform a regex match on the tag.
    """
    if pattern[0] == '~':
        return not re.search(pattern[1:], tag)
    return re.search(pattern, tag)
