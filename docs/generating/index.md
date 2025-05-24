---
layout: default
title: "Generating & Preparing for the Mojo Tutorials using Pocket Flow"
nav_order: 8
---

This gives the details of how the Mojo tutorials (as the sanity check tutorial) were generated using Pocket Flow and how to prepare yourself for that usage of Pocket Flow.

REF: [Clean Run of The Mojo Tutorial version 2](./clean_run.md)


## Warmups, Exercises and Sanity Checks

Before tackling a huge, new repo from Modular with a very new, highly abstract framework like Pocket Flow, I took some baby steps.

### Warming up with the Difficulties of the Pocket Flow Demo

I had many difficulties with Pocket Flow which I now blieve are largely Pocket Flow itself is new. I complained at length with both Perplexity and also with OpenAI:
- [long-winded inquiry with Perplexity Research](https://www.perplexity.ai/search/3f2e2e35-45fc-4ac2-8556-b4a6d5ef6540)
- [far more consice Page report from Perplexity of the long-winded chat](https://www.perplexity.ai/page/questions-about-pocketflow-llm-j2Wg1rCdSbO3F2prOGIQig)
- [OpenAI’s Quick, Pointed Reply with o4-mini-high](https://chatgpt.com/share/6827620e-0800-800d-a83c-e216698046d6)

### Preliminary Exercise with the Pocket Flow Demo in Zach's: [Pocket Flow Cookbook](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook)

The biggest difficulty I had was difficulty the `.ipynb` demo in Cursor and undertook to develop each of its 4 parts as individual demos. Using a different notebook server in Cursor is likely a viable option, but I did not pursue that.
- I honestly don't like NoteBooks and prefer the more old-fashioned, file-oriented style of development.
- It was a successful training exercise.  Part 4 of 4 was the most difficult.

I did this initial prompt in Cursor using Sonnet 3.7 MAX with Zach's CookBook:
```
You an expert in PocketFlow, i.e., Zachary Huang who developed PocketFlow. What kind of a graph in PocketFlow would you create to implement a RAG chatbot that, given a user’s input question, finds the most relevant file based on embeddings and then answers the user's question. Test it with a shared store that has preloaded all text files from @/Users/sam/Projects/the-pocketflow/cookbook/data/PaulGrahamEssaysLarge.
```
and followed it up with:
```
Great. Now integrate all the Python code you created into a single file along with the required utilities.
```
The chatbot in Cursor generated `rag_chatbot.py`. After some struggles with `init/call_llm.py` using a Sonnet model for its API purposes, I finally got a good result:
```
(venv) (base) sam@Samuels-MacBook-Pro the-pocketflow % python rag_chatbot.py
--- Starting Indexing Phase ---
Loaded 5 documents
Created 101 chunks from 5 documents
Generated 101 embeddings
Index created with 101 chunks and 101 embeddings
Documents indexed: {'addiction.txt', 'apple.txt', 'before.txt', 'avg.txt', 'aord.txt'}

--- Starting Query Phase ---
Enter your question: What's the best way to get an idea for a startup?
Question: What's the best way to get an idea for a startup?
Retrieved chunks from: ['before.txt', 'before.txt', 'before.txt']

Answer: Turn your mind into the type that startup ideas form in without any conscious effort.

--- Query Complete ---
``` 

### A Preliminary Sanity Check: Hello World

From his CookBook (#TODO Ref?), I also did the Hello World example:

1. **pocketflow-hello-world**: Basic starter example showing simple question-answering with minimal PocketFlow implementation.
2. **pocketflow-rag**: Demonstrates Retrieval Augmented Generation with document chunking, vector embeddings, and relevant content retrieval for better LLM responses.
3. **pocketflow-agent**: Implements a decision-making research agent that can search the web and decide when to seek more information versus answering directly.
4. **pocketflow-batch**: Shows batch processing for translating content into multiple languages simultaneously, demonstrating parallel task handling.
5. **pocketflow-multi-agent**: Implements async communication between two AI agents playing a Taboo word guessing game, showcasing complex agent interactions.
6. **pocketflow-flow**: Likely demonstrates basic flow creation and management in PocketFlow.
7. **pocketflow-node**: Probably focuses on creating and using different node types.
8. **pocketflow-chat**: Simple chatbot implementation showcasing conversation handling.
9. **pocketflow-chat-memory**: Enhanced chatbot with conversation history/memory capabilities.
10. **pocketflow-chat-guardrail**: Chatbot with safety guardrails and content filtering.
11. **pocketflow-tool-** series (crawler, database, embeddings, pdf-vision, search): Examples of integrating various external tools with PocketFlow.
12. **pocketflow-text2sql**: Converts natural language to SQL queries using LLMs.
13. **pocketflow-map-reduce**: Implements the MapReduce pattern for parallel data processing and aggregation.
14. **pocketflow-async-basic**: Shows basic asynchronous operations within PocketFlow.
15. **pocketflow-parallel-batch**: Demonstrates running multiple batch processes in parallel.
16. **pocketflow-structured-output**: Examples of getting structured data (JSON/YAML) from LLMs.
17. **pocketflow-visualization**: Tools for visualizing PocketFlow graphs and execution.
```
(venv) pocketflow-hello-world % python main.py       
Question: In one sentence, what's the end of universe?
Answer: The end of the universe could manifest as the "heat death," where it reaches a state of maximum entropy and no thermodynamic free energy remains to sustain processes, leading to darkness and uniformity.
```

### The Final Sanity Check: Crawl4AI

Ramping up to bigger Pocket Flow runs, I reviewed the tutorials in [Zach's repo](#TODO)

I chose Craw4AI because it seemed to me to be the most ordinary of purpose, i.e., it was quite pedestrian. (No pun intended. 😃).

## Generating the Mojo Tutorials
In a separate project folder, I simply cloned the Modular repo and switched to the stable branch per their recommendations:
```
TBD
```


#TODO - Eventually, when reading my Obisidan notes, I will come across the details for the comparisons I made and puts them into the two files in the `Comparisons/` folder.



I used Python 3.12.7 with `venv`.

