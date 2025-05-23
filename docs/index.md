---
layout: default
title: "Home"
nav_order: 1
---

# Turns Codebase into Easy Tutorial - Pocket Flow

Ever stared at a new codebase written by others feeling completely lost? This project analyzes GitHub repositories and creates beginner-friendly tutorials explaining exactly how the code works - all powered by AI! Our intelligent system automatically breaks down complex codebases into digestible explanations that even beginners can understand.

<p align="center">
  <a href="https://github.com/The-Pocket/PocketFlow" target="_blank">
    <img 
      src="https://raw.githubusercontent.com/The-Pocket/Tutorial-Codebase-Knowledge/refs/heads/main/assets/banner.png" width="800"
    />
  </a>
</p>

# PF-Understand Documentation

Welcome to the documentation for PF-Understand, a tool for generating comprehensive tutorials from codebases.

## Tutorials

All in all, I did 4 fairly complete runs of Pocket Flow tutorializing abstractions.

- [Crawl4AI](./Crawl4AI/) - The original tutorial already done in Pocket Flow's repo
- [My Crawl4AI](./my-crawl4ai/) - My sanity check run for an that repo
- [Modular Max](./modular_max/) - When doing the entire Modular repo, it chose to do Max Engine, ignoring Mojo almost entirely.
- [Mojo v1](./mojo-v1/) - When focusing Pocket Flow on just the mojo folder in Modular's repo, a tutorial on its high-performance multi-dimensional array operation
- [Mojo v2](./mojo-v2/) - The final run of Pocket Flow which ran smoothly (no errors in about 1.75 hours) on resulted in a different tutorial for Mojo, this time focusing on Mojo's N-dimensional data structures

Using gemini-2.5-pro in Cursor, I did the following two comparisons:
- TBD: the first run above, sanity check on [Crawl4AI](./crawl4ai/) in the exisitng repo in `output/crawl4ai/`.
- TBD: the last two runs above, the two different versions of tutorials for Mojo.
I also did a comparison 

## Other notes TBD


