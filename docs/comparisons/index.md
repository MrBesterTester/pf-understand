--
layout: default
title: "Comparisons"
nav_order: 7
---

To REALLY assess the tutorials I wrote, the simple, straightforward way to do that would be take those tutorials and see how it goes. In engineering, this is called "eating your own dog food."

I did not do that, "leaving that as an exercise for the reader" and deferring it later.

I did, however, apply gemini-2.5-pro to check the versions of turtorials.  In essence this a consistency check rather than a full-flow QA assessment.

# Comparisons of Different Versions of Tutorials

I did two comparison:

## [The original version of Crawl4AI vs. the sanity check I did](./crawl4ai-versions.md)

The sanity check version had a different number of chapters with differing titles. To do manual comparison would have been quite painstaking.  So I left it up to AI.  I think gemini-2.5-pro did a good job

## [The 1st version of the Mojo Tutorial vs. The 2nd version of the Mojo Tutorial](./mojo-versions.md)

What happend when I intially did the tutorial on the entire Modular repo, is that I got a tutorial focusing on the MAX Engine.  Not a bad tutorial, but, surprisingly, really mention of Mojo.

So I focused on just the `mojo/` folder in the Modular repo.
- First time through (verison 1), I worked out many of the drawbacks (mainly GitHub and Gemini rate limits hits) in `init/call_llm.py`.
- Second time  through (version 2), was the final run that went cleanly from beginning to end. I took about 1.75 hours and cost about $12 in Gemini time on Google.
    - I spent about $32 in total.

I spent about as much time getting the final clean run as I have in writing up the tutorial per Just The Docs as a GitHub Page.
- Running the local rendering before pushing it to GitHub is quite essential.
```
```
- Switching back and forth beween `theme` to `remote_theme` in `_config.yml` is highly annoying.

Here's the [console log of the final run](#TODO)


