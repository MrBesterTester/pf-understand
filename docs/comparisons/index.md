---
layout: default
title: "Comparisons"
nav_order: 7
has_children: true
---
## Comparisons of Different Versions of Tutorials

To REALLY assess the tutorials I wrote, the simple, straightforward way to do that would be take those tutorials and see how it goes. In engineering, this is called "eating your own dog food."

However, I did not do that and "leave that as an exercise for the reader," deferring that as another separate project.

I did, however, apply gemini-2.5-pro to check the versions of turtorials.  In essence this a consistency check rather than a full-flow QA assessment.

So, I did two comparisons:

### [The original version of Crawl4AI vs. the sanity check I did](./crawl4ai-versions)

The sanity check version had a different number of chapters with differing titles. To do manual comparison would have been quite painstaking.  So I left it up to AI.  I think gemini-2.5-pro did a good job.
- I enjoyed the analogies used in the version of my tutorial.

### [The 1st version of the Mojo Tutorial vs. The 2nd version of the Mojo Tutorial](./mojo-versions)

What happend when I intially did the tutorial on the entire Modular repo, is that I got a tutorial focusing on the MAX Engine: [My Tutorial for Modular's Max](../modular_max/)  Not a bad tutorial, but, surprisingly, no mention of Mojo.

So I focused on just the `mojo/` folder in the Modular repo.
- First time through (verison 1), I worked out many of the drawbacks (mainly GitHub and Gemini rate limits hits) in `init/call_llm.py`.
- Second time  through (version 2), was the final run that went cleanly from beginning to end. I took about 1.75 hours and cost about $12 in Gemini time on Google.
    - I spent about $32 in total for Gemini time on Google.

Nevertheless, gemini-2.5-pro shined again making a comparison between the first and second versions .

Here's the [console log of the final run](../generating/clean_run)

For more details about developing the tutorials see [Generating and Preparing the Mojo Tutorials using Pocket Flow](../generating/)
