---
layout: default
title: "Generating & Preparing for the Mojo Tutorials using Pocket Flow"
nav_order: 8
---
## Generating & Preparing for the Mojo Tutorials using Pocket Flow

This Chapter gives the details of how the Mojo tutorials (as well as the sanity check for a complete tutorial) were generated using Pocket Flow and how to prepare yourself for that usage of Pocket Flow.

### Warmups, Exercises and Sanity Checks
Before tackling a huge, new repo from Modular with a very new, highly abstract framework like Pocket Flow, I took some baby steps.

#### Warming up with the Difficulties of the Pocket Flow Demo

I had many difficulties with Pocket Flow which I now believe are largely because Pocket Flow itself is new. I complained at length with both Perplexity and also with OpenAI:
- [long-winded inquiry with Perplexity Research](https://www.perplexity.ai/search/3f2e2e35-45fc-4ac2-8556-b4a6d5ef6540)
- [far more concise Page report from Perplexity of the long-winded chat](https://www.perplexity.ai/page/questions-about-pocketflow-llm-j2Wg1rCdSbO3F2prOGIQig)
- [OpenAI’s Quick, Pointed Reply with o4-mini-high](https://chatgpt.com/share/6827620e-0800-800d-a83c-e216698046d6)

#### Preliminary Exercise with the Pocket Flow Demo in Zach's: [Pocket Flow Cookbook](https://github.com/The-Pocket/PocketFlow/tree/main/cookbook)

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

#### A Preliminary Sanity Check: Hello World

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

#### The Final Sanity Check: Crawl4AI

Ramping up to bigger Pocket Flow runs, I reviewed the tutorials in [Zach's repo](#TODO)

I chose Craw4AI because it seemed to me to be the most ordinary of purpose, i.e., it was quite pedestrian. (No pun intended. 😃).

I used Python 3.12.7 with `venv`, running an Intel MacBook 2018 with 32GB RAM on macOS Sequoia 15.5.

The version of Pocket Flow that I cloned as `~/Projects/pf-understanding`:
```
2afe6f696ae9f30eda2423f8a5d2453fdfa3e9d1
Merge pull request #112 from rossdonald/utf-bom-handling
fix: update file opening encoding to utf-8-sig to handle files with BOM
```
And then simply ran:
```
 (venv) Pro pf-understand % pip install -r requirements.txt
 (venv) Pro pf-understand % pip install --upgrade pip
```
To generate my version of the Crawl4AI tutorial:
```
python main.py --repo https://github.com/unclecode/crawl4ai --include "*.py" --exclude "tests/*" "docs/*" --max-size 30000
```
taking only just under 14 minutes. For this run I used Claude Sonnet 3.7 in `utils/call_llm.py`.

The results are [My Tutorial for Crawl4AI](../my-crawl4ai/).

## Generating the Mojo Tutorials

In a separate, sibling project folder, `~/Projects/modular`, I simply cloned the Modular repo and switched to the stable branch per their recommendations:
```
modular % git clone https://github.com/modular/modular.git
modular % git checkout stable
```
The version of Modular's software I used is v25.3.0
```
modular % git describe --tags
modular/v25.3.0
```
More specifically according to the branch history in Cursor:
```
modularbot,  3 weeks ago (May 6, 2025 at 11:39 PM)
[Release] Update lockfiles to point to latest stable version: 25.3.0
15 files changed, 16275 insertions(+), 16108 deletions(-)
```

There were 3 runs on Modular software I did. 
1. [Modular Max](../modular_max/)
2. [Mojo v1](../mojo-v1/)
3. [Mojo v2](../mojo-v2/)

The Modular Max was done using a the GitHub repo on the web, whereas the Mojo tutorials were done with a cloned repo on my computer in an effort to speed things up and avoid GitHub rate limit hits.

Further, because the the Modular Max tutorial wasn't getting anything about Mojo, I used the clone of Modular's repo and focused on just the `mojo` folder in the Modular repo.

Version 1 was the debugging run. I'm not about to try to even try to summarize the blow-by-blow, very lengthy discussion with Sonnet 3.7 MAX that I had in Cursor.  It would be best to simply read the API header block doc string in `util/call_llm.py`. I believe I have vastly improved it w.r.t. gemini-2.5-pro and may have made a mini version of langchain.

Version 2 is the clean run.  The winning command for the clean run:
```
time python main.py --dir "~/Projects/modular/mojo" --include "*.mojo" "*.🔥" "*.py"  --exclude "tests/* " "proposals/*" --max-size 200000
```
taking 1 hour, 42 minutes. The glorious screen dump from the generation of the clean run is [here](./clean_run). 

I counted 257,604 files in the `mojo/` folder: 
```
mojo %find . -type f -name "*.mojo" -exec wc -l {
} \; | awk '{total += $1} END {print total}'
```
However, Pocket Flow consistently said it scanned only about 525 files. See [clean run of version 2 of the Mojo tutorial](./clean_run).

I paid:
- Google about $30 for use of running gemini-2.5-pro with Pocket Flow
- GitHub about $25 for the priviledge of publishing a GitHub page and keepng it private on GitHub (but not web search)

## Generating Just The Docs

### Meta Document Strategy
The name of the game for writing up documentation is that you can reproduce my results.  There is, however, a complicating factor: said documentation is about the generation of documents, in this case, by Pocket Flow.
- So that means keeping the documents I write here as meta-documents for those generated by Pocket Flow and not mixing or confusing the two.

I have done so by keeping the generated documents in the Just The Documents table of contents near the top except for a brief introduction at the very top as the Home page (top-most index.md file).

### Routine Just The Docs Generation

Running Just The Docs **locally** is very helpful because doing the GitHub build for the Just The Docs Page is time-consuming:
1. Clone the repository
2. Install Ruby and Bundler
3. Run `bundle install`
4. cd `docs/` and run `bundle exec jekyll serve` 
5. Push to GitHub after enabling GitHub Pages in repository settings. 

Running the local rendering before pushing it to GitHub is quite essential. Once the above procedure is done, just loop on step 4.
- Make sure you're in the `docs/` folder
- and that you're in the `venv` environment.

Also, intially, I had kept my generated output in the `output/` folder, but later revised `docs/` as this seemed to be more amendable to Just The Docs.

The **first** part of the last step, step 5, is easily done by usual raindance for pushing changes up the GitHub repo:
```
 git pull --rebase origin main
 git push -u origin main
```

I really had some difficulty with that the **last** part of the last step, step 5, getting Just The Docs to setup **remotely** my repo up as a Page on GitHub: [You are an expert in posting and publishing repo on GitHub.com...](https://www.perplexity.ai/search/40d35332-eae7-45fd-9256-aca03838f899)
- The GitHub chatbot was fairly helpful, however, and seemed to be quite familiar with the problem I was having:
1. Go to your GitHub repository
2. Click on "Settings" 
3. Select "Pages" from the sidebar
4. Under "Build and deployment" > "Source", select "Deploy from a branch"
5. Choose "main" branch and "/docs" folder
6. Click "Save"

Although getting the final clean run was a real drag, I spent far more time in writing up the tutorial per Just The Docs as a GitHub Page. But any documentation format would still have been about as tedious because documentation is always slow pain.

Once the build procedure for Just The Docs to create the GitHub page is done once, it is automatic from thereon, *except*:
- Switching back and forth in `_config.yml` between `theme` for the local rendition  and to `remote_theme` for the GitHub Page is highly annoying.

The good news is that once the bugs are with Just The Docs are worked out locally they always work remotely on GitHub after the build job runs there.
- To check for the Pages build job, look under the Actions tab on the Settings for your repo on GitHub.