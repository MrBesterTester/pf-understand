---
layout: default
title: "README"
nav_order: 1
---

This repo applies the [Pocket Flow](https://the-pocket.github.io/PocketFlow/) framework by Zachary Huang to the Mojo programming language and other tools created by Modular AI for the purpose of creating tutorials about the Mojo programming language.
- The repo for Zachary's code is: [Pocket Flow - LLM Framework in 100 lines of Code](https://github.com/the-pocket/PocketFlow)
- Zachary has number of YouTube videos explaining his framework. My favorite is: [I built PocketFlow! 100-Line LLM framework to Let Agents Build Agents for You](https://www.youtube.com/watch?v=0Pv5HVoVBYE&list=PLE7QL88ze7c4GUz3lxpsYHyuYG9NFya0K&index=3) 

The target of my application is [The Mojo programming language](https://github.com/modular/modular) developed by [Modular AI](https://www.modular.com).  It is a very new programming language, intially built to solve the problem of programming Graphical Processing Units (GPUs) as well as the more general problem of heterogeneous programming.
- Having conquered the problem of programming nVidia GPUs, Modular recently announced their support of AMD GPUs in a Hackathon about two weeks ago.
- Because it is quite new, it's repertoire does not yet fall into the domain of the big LLMs to the best of my knowledge because their trainers have not had the time to use the newly released 650K SLOC on GitHub.

In this repo, I have undertaken to develop a training course (or similar material such as a reference guide) to Mojo by unleashing Zach's profound abstractions in his Pocket Flow framework directly upon Mojo's GitHub repo.
- In addition to the Mojo compiler, there are other important tools that Modular offers, notably the MAX execution enginer which allows you to run the Mojo GPU kernels on a very wide range of LLMs very efficiently with very high performance.
- I also really like their `magic`, their package manager based heavily on [pixi](https://pixi.sh/latest/).
- Additionally, Modular has released Mojo in on PyPi so that it can be installed using Python's `pip` program.

In this repo, I did not use `magic` nor did I install Mojo with `pip`. I simply cloned Pocket Flow to scan Modular's code on GitHub after cloning it as well to generate Pocket Flow tutorials about Modular's code.

## My Pocket Flow Tutorials

All in all, I did 4 fairly complete runs of Pocket Flow tutorializing abstractions, 3 of which were on the Mojo repo, the first of which was a sanity check:

- [Crawl4AI](./Crawl4AI/) - The original tutorial already done in Pocket Flow's repo
- [My Crawl4AI](./my-crawl4ai/) - My sanity check run for an that repo
- [Modular Max](./modular_max/) - When doing the entire Modular repo, Pocket Flow chose to do Max Engine, ignoring Mojo almost entirely.
- [Mojo v1](./mojo-v1/) - When focusing Pocket Flow on just the mojo folder in Modular's repo, it generated a tutorial on Mojo's high-performance multi-dimensional array operation.
- [Mojo v2](./mojo-v2/) - The final run of Pocket Flow which ran smoothly (no errors in about 1.75 hours) on resulted in a different tutorial for Mojo, this time focusing on Mojo's N-dimensional data structures

As an alternative to doing a complete assessment those tutorials I generated, I using gemini-2.5-pro in Cursor to do comparisons of the two versions of Crawl4AI tutorials and also for the two versions fo the Mojo tutorials:
- [Comparison of Versions](./comparisons/)

The inadvertent tutorial on [Modular Max](./modular_max/) has only 1 version.

## Usage of the Mojo Tutorial

To use any of these tutorials, simply click on the link above or in the side bar and follow along.  Some include coding exercises and some are conceptual guides with coding examples.  Please read the [Comparison of Versions](./comparisons/) before diving in.

## Generating the Mojo Tutorials

If you're a software developer see [Generating & Preparing for the Generation of the Mojo Tutorials using Pocket Flow](./generating/)

Note that the chapter on [System Design](./design.html) was left over from Zachary's original repo.  That file is referenced in `.cursorrules` files and because I used Cursor exclusively that file was used throughout all the tutorial generation I did.






