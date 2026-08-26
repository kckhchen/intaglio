import re

from src.patterns import BLOCK_MATH_PATTERN, INLINE_MATH_PATTERN, MATH_ID_PATTERN

MATHJAX = '<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@4/tex-mml-chtml.js"></script>'


def process_math(post, math_rendering_mode):
    if _needs_math(post.content):
        post.content = re.sub(INLINE_MATH_PATTERN, r"\\\\(\1\\\\)", post.content)
        post.content = re.sub(
            BLOCK_MATH_PATTERN, r"\n\1\n", post.content, flags=re.DOTALL
        )

        if math_rendering_mode == "inject_cdn":
            post.content += f"\n\n{MATHJAX}"
        elif math_rendering_mode == "metadata":
            post["math"] = post.get("math") or True

        post = _fix_math_id(post)

    return post


def _needs_math(content):
    has_block_math = bool(re.search(BLOCK_MATH_PATTERN, content, flags=re.DOTALL))
    has_inline_math = bool(re.search(INLINE_MATH_PATTERN, content))

    return has_block_math or has_inline_math


def _fix_math_id(post):
    # this is needed since anochors of math blocks should be exactly one line below the $$.
    post.content = re.sub(MATH_ID_PATTERN, r"$$\n\1", post.content)

    return post
