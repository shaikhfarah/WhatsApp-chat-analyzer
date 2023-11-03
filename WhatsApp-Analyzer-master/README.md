# WhatsApp-Analyzer
Analyze WhatsApp chat

The script reads an exported WhatsApp chat and then extracts the data. You may need to install some packages before running it.

##### Supported Analysis
----------------------
- Chat Count
- Chat Average
- Member/Sender Rank
- Website/URL/Link Domain Rank
- Word Count and Rank
- Most Used Word by Sender
- Emoji Usage Rank
- Most Used Emoji by Sender
- Timestamp Heatmap
- Attachment Classification (In Android, there is no difference pattern for attachment. But in iOS we can actually classify between Image, Video, Audio, GIF, Sticker, Document and Contact Card)



### Requirements
----------------------
- Python 3.6+
```python
pip install -r requirements.txt
```


```shell
usage: python whatsapp_analyzer.py FILE [-h] [-d] [-s] [-c]

Read and analyze whatsapp chat

positional arguments:
  FILE                  Chat file path

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           Debug mode. Shows details for every parsed line.
  -s , --stopword       Stop Words: A stop word is a commonly used word (such
                        as 'the', 'a', 'an', 'in'). In order to get insightful
                        most common word mentioned in the chat, we need to
                        skip these type of word. The Allowed values are:
                        arabic, bulgarian, catalan, czech, danish, dutch,
                        english, finnish, french, german, hebrew, hindi,
                        hungarian, indonesian, italian, malaysian, norwegian,
                        polish, portuguese, romanian, russian, slovak,
                        spanish, swedish, turkish, ukrainian, vietnamese
  -c , --customstopword 
                        Custom Stop Words. File path to stop word. File must a
                        raw text. One word for every line
```
### Stop Words
----------------------
I've included stop words for several languages from https://github.com/Alir3z4/stop-words.
You can use your own stop word file.
Just use `-c` argument followed by filepath.
One word for each file like below
```
able
ableabout
about
above
abroad
abst
```





## Flowchart
----------------------
Describe how the script identify and classify the chat
```
           +------------------+
      +----+    Empty line?   +----+
      |    +------------------+    |
      |                            |
      |                            |
  +---v---+                   +----v---+
  |  Yes  | +-----------------+   No   |
  +-------+ |                 +---+----+
            |                     |
  +---------+-+             +-----v-----+
  | Event Log |        +----+    Chat   +----+
  +-----------+        |    +-----------+    |
                       |                     |
                +------v-----+         +-----v------+   +--------------------+
          +-----+Regular Chat+----+    | Attachment +-->+ Clasify Attachment |
          |     +------------+    |    +------------+   +-------+------------+
          v                       v                             |
+---------+---------+   +---------+----------+                  |
|   Starting Line   |   |   Following Line   |                  |
+------+------------+   +-+------------------+                  |
       |                  |                                     |
       |                  |                                     |
       |           +------v-------+                             |
       |           | COUNTER      |                             |
       |           | 1 Chat       |                             |
       +---------->+ 2 Timestamp  +<----------------------------+
                   | 3 Sender     |
                   | 4 Domain     |
                   | 5 Words      |
                   | 6 Attachment |
                   | 7 Emoji      |
                   +-----+--------+
                         |
                         |
                         |
                         v
              +----------+----------------+
              |          Visualize        |
              +---------------------------+
```


### Getting chat source
#### Android:
- Open a chat/group chat
- Tap on three dots on the top right
- Tap "More"
- Choose "Export chat"
- Choose "Without Media"

#### iOS
- Open a chat/group chat
- Tap on contact name/group name on the top to see the details
- Scroll down to find "Export Chat" menu
- Choose "Without Media"


