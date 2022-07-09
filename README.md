# Auto-Zlapp

## Attention

The original code is from https://github.com/FDUCSLG/pafd-automated, while the code in this repo has been optimized, and a new function of sending message to WeChat by [PushPlus](https://www.pushplus.plus/) is added. It should be emphasized that the author created this repo mainly to learn web program at first; though the desire to win the competition with her girlfriend's boyfriend may also be a factor as time went by, the function of auto zlapp is always the least important reason.

## Programming Requirements

- `time`: to get today's date;
- `os`: to get environment variables and manage files;
- `logging`: to get log files;
- `string`: to get strings;
- `re`：to match strings;
- `json`: to load strings as dictionaries;
- `getpass`: to get password from keyboard input;
- `easyocr`: to read captcha;
- `io`: to convert the type of image data;
- `numpy`: the same as above;
- `PIL`: to enhance image;
- `requests`: to manage the webpage.

## User Installation

### GitHub Action (Recommended)

1. Fork this repo;

2. In one's own repo, follow `Setting`, `Secrets`, `Actions`;

3. Create 3 new secrets, which will be kept confidential by GitHub;

   | Number | Name             | Value                    |
   | ------ | ---------------- | ------------------------ |
   | 1      | `FUDAN_ID`       | One's Fudan UIS ID       |
   | 2      | `FUDAN_PASSWORD` | One's Fudan UIS Password |
   | 3      | `PUSHPLUS_TOKEN` | One's PushPlus Token     |

4. Then GitHub Action will help one to zlapp according to history information at 10 a.m. every day.

### Windows10 Trigger (Not Recommended)

First, convert the python script to a executable file using the following command:

```bash
pip install pyinstaller
pyinstaller -F zlapp.py
```

Then the following files will be built:

```
build/zlapp/...
dist/zlapp.exe
zlapp.spec
```

Only `zlapp.exe` matters for us, which we should build a trigger on, following the [link](https://zhuanlan.zhihu.com/p/115187442).

After building the trigger, there are several things one may confirm:

- whether the trigger can always run, instead of just when the computer is in charge;
- whether one have the privilege to run a trigger, with reference to the [link](https://blog.csdn.net/SmileLvCha/article/details/119563178) or to the Windows official website.
