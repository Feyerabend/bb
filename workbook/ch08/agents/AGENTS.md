
## Commentary on "Active agents and other concepts" (1997)

This text was written in 1997 and explores the emerging landscape of distributed computing.
While the phrasing may at times appear dated or slightly unpolished--my native language is
*not* English--the core ideas are surprisingly prescient, even to the current me. It touches
on paradigms that would go on to shape the internet era and continue to influence computing
today. Let's explore.

*Here is a commentary by Gemini, Flash 2.5.*


### Active Agents: A Vision of Autonomous Software

The author’s primary focus on "active agents" immediately stands out. The analogy of "human
agents that travel between countries" to describe software that "travels between 'machines'"
is a powerful and intuitive metaphor for mobile agents. This concept—software entities that
could migrate, execute tasks remotely, and report back—was a significant area of research
and development in the mid-90s.

The text astutely distinguishes between agents restricted by protocols and those "free to do
non-anticipated actions." This distinction is critical: the former describes highly controlled,
deterministic processes, while the latter hints at true autonomy and emergent behavior. While
the mobile agent paradigm of the 90s (like early Java-based agents) didn't achieve widespread
commercial dominance due to challenges in security, standardization, and the rise of more
centralized web architectures, the *idea* of autonomous, task-oriented software entities has
seen a powerful resurgence. Today's AI-driven agents, particularly those leveraging Large
Language Models (LLMs), embody the "non-anticipated actions" concept, acting with a degree of
freedom and decision-making capability across various tools and services. The text's early
recognition of this potential is quite remarkable.


### Client-Server vs. Terminal-Server: Enduring Architectures

The clear differentiation between "client-server" and "terminal-server" models highlights a
fundamental architectural debate of the era. The client-server model, where "some of the
executing software is at the client, and some at the server," underpins the vast majority
of web applications and distributed systems today (e.g., your browser interacting with a
cloud service).

The "terminal-server" model, where "almost everything is supposed to be done by the server"
and the client is "dumb," was seeing a resurgence in 1997 (as hinted by "thin clients" or
"instant operating system download"). This prediction was spot-on. Thin clients, virtual
desktops (VDI), and later, Chromebooks and cloud-streaming services, validated the continued
relevance of this centralized processing model, particularly in managed environments or for
resource-constrained devices.

The author's conclusion that "both developments occur at the same time" and that "connections
have to get smarter and local computing has to get more enriched" is profoundly accurate.
We now operate in a highly hybrid world: rich local applications coexist with cloud-native
services, and edge computing merges local processing with distributed networks. The text
correctly foresaw a landscape of coexisting, rather than mutually exclusive, architectural
paradigms.


### Push and Pull Technology: Anticipating Real-Time Web

The analysis of "pull technology" (the web, where you "asked for 'information'") versus "push
technology" (email, where "information" is sent to you) is a sharp observation for its time.
The mention of "push technology" being "added to the web" around 1997 is highly prescient.
This refers to early attempts at server-initiated updates, which would later mature into
fundamental web technologies like WebSockets, Server-Sent Events, and the pervasive push
notifications we experience daily.

The author’s critical assessment—that the "social implications (and communicational)... are
however not new" and that the "difference is not a giant leap"—is a valuable dose of skepticism.
It reminds us that underlying human communication patterns often predate new technologies,
which primarily offer new *mechanisms* for those patterns. This sober view on technological
hype remains relevant in any era of rapid innovation.


### Market Forces and Strategic Alignment

The text accurately identifies how "market forces" dictate technology adoption. The specific
examples of Microsoft favoring "local machines" (due to its Windows OS dominance) and Sun
Microsystems pushing "servers and connections" (reflecting its "network is the computer"
Java-centric philosophy) perfectly capture the strategic tensions of the mid-90s.

The prediction that both models would "proceeding in the right direction" and that "most
probable thing is that both developments occur at the same time" proved absolutely correct.
Microsoft adapted heavily to the server and cloud space (Azure), and Sun's network-centric
vision found echoes in cloud computing, even if Sun itself eventually faded as an independent
hardware innovator. This part of the text demonstrates a keen understanding of the interplay
between technology, business models, and market competition.


### Agents as an "Off-Line Paradigm": A Vision Beyond Interactive Web

Perhaps the most conceptually ambitious part of the text is its final section, proposing
"intelligent agents that travel" as an alternative to "interactive connections." The idea
that "the task can be given at one time and the reply returned much later" and that agents
"work independently of the originator" directly points to the need for an "off-line paradigm"
that "the web isn't the most suitable, because of its inherent interactive aspect."

This foresight into decoupled, asynchronous communication is profound. It anticipates the
widespread adoption of:
- *Message Queues (e.g., Kafka, RabbitMQ):* Systems where tasks are placed in a queue to
  be processed independently.
- *Event-Driven Architectures:* Where systems react to events rather than requiring constant,
  interactive communication.
- *Offline-First Applications:* Mobile apps that function without an immediate connection,
  syncing data when connectivity is restored.
- *Serverless Computing:* Functions that execute in response to events, without persistent servers.

The author's recognition of the limitations of purely interactive, "on-line" systems and the
need for a complementary, asynchronous model, is a testament to their deep conceptual understanding
of distributed systems' future needs.


### Conclusion

This 1997 text is an exceptionally valuable historical document. Its author possessed a rare
combination of technical insight, philosophical depth, and market awareness. While the language
might require some interpretation for a modern audience, the core ideas—the potential of
autonomous agents, the enduring relevance of different architectural styles, the evolution
of push/pull technologies, and the necessity of asynchronous "off-line" paradigms—have proven
remarkably accurate. It serves as a powerful reminder that fundamental challenges and solutions
in computing often cycle and reappear, albeit in new technological guises, driven by underlying
human needs and market forces.


